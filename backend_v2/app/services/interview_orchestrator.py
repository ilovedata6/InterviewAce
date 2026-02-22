import logging
from typing import List, cast
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.interview import InterviewSession, InterviewQuestion
from app.schemas.interview import InterviewQuestionCreate, SummaryOut, QuestionFeedback
from app.db.session import get_db
from app.core.config import settings
from app.domain.interfaces.llm_provider import ILLMProvider
from app.infrastructure.llm.factory import get_llm_provider
from app.models.resume import Resume
from app.models.user import User
from fastapi import HTTPException, status
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class InterviewOrchestrator:
    def __init__(self, db: Session, llm_provider: ILLMProvider | None = None):
        self.db = db
        self.llm_provider = llm_provider or get_llm_provider()

    def fetch_resume_context(self, resume_id: UUID) -> dict:
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume with ID {resume_id} not found")

        # Extract relevant context
        experience = resume.analysis.get("experience", [])
        projects = [
            {
                "description": exp.get("description", "No description available")
            }
            for exp in experience
        ]

        return {
            "inferred_role": resume.inferred_role,
            "years_of_experience": resume.years_of_experience,
            "skills": resume.skills,
            "projects": projects
        }

    def generate_questions(self, session: InterviewSession, resume_context: dict) -> List[InterviewQuestionCreate]:
        try:
            logger.info(f"Generating questions for session {session.id} with context: {resume_context}")
            prompt = self._build_prompt(resume_context)
            questions = self.llm_provider.generate_questions(prompt)
            logger.info(f"LLM response for session {session.id}: {questions}")
            return self._map_questions_to_schema(cast(UUID, session.id), questions)
        except Exception as e:
            logger.error(f"LLM call failed for session {session.id}: {e}")
            raise

    def _build_prompt(self, resume_context: dict) -> dict:
        inferred_role = resume_context.get("inferred_role")
        years_of_experience = resume_context.get("years_of_experience")
        skills = resume_context.get("skills", [])
        if not isinstance(skills, list):
            skills = []
        projects = resume_context.get("projects", [])[:4]

        project_details = "\n".join(
            [f"Projects: {p['description']}" for i, p in enumerate(projects)]
        )
        
        system_prompt = (
                "You are an expert technical interviewer. "
                "Your job is to generate a list of high-quality, on-point interview questions "
                "that test a candidate's skills, professional experience, and past projects. "
                "Always respond with valid JSON only."
)
        
        user_prompt = (
                    f"Candidate Profile:\n"
                    f"- Role: {inferred_role}\n"
                    f"- Years of Experience: {years_of_experience}\n"
                    f"- Skills: {', '.join(skills)}\n"
                    f"- Projects:\n{project_details}\n\n"
                    "OUTPUT FORMAT:\n"
                    "- Return a JSON array of objects, each with:\n"
                    "    { \"type\": \"technical|behavioral|project\", \"question\": string }\n"
                    "- Total questions: 12–15\n"
                    "- Counts: 5 technical, 3 behavioral, 5–4 project\n"
                    "- No additional text, no markdown, no code fences.\n\n"
                    "Now generate the questions."
)

        return {
            'system_prompt': system_prompt,
            'user_prompt': user_prompt
        }

    def _map_questions_to_schema(self, session_id: UUID, questions: List[str]) -> List[InterviewQuestionCreate]:
        return [InterviewQuestionCreate(session_id=session_id, question_text=q) for q in questions]

    def persist_questions(self, session: InterviewSession, questions: List[InterviewQuestionCreate]):
        logger.info(f"Persisting {len(questions)} questions for session {session.id}")
        for question_schema in questions:
            question = InterviewQuestion(
                session_id=question_schema.session_id,
                question_text=question_schema.question_text
            )
            self.db.add(question)
        self.db.commit()
        logger.info(f"Successfully persisted questions for session {session.id}")

def get_user_session(db: Session, user: User, session_id: UUID):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if session is None:
        return None
    if str(session.user_id) != str(user.id):
        return None
    return session

def get_next_question(db: Session, session: InterviewSession):
    return (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.session_id == session.id, InterviewQuestion.answer_text == None)
        .order_by(InterviewQuestion.created_at)
        .first()
    )

def submit_answer(db: Session, session: InterviewSession, question_id: UUID, answer_text: str):
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id,
        InterviewQuestion.session_id == session.id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found or not in session")
    question.answer_text = answer_text  # type: ignore
    db.commit()
    next_question = get_next_question(db, session)
    return next_question

def complete_interview_session(db: Session, session: InterviewSession):
    # Fetch all questions for the session
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).all()
    if not questions:
        raise HTTPException(status_code=400, detail="No questions found for this session.")
    unanswered = [q for q in questions if q.answer_text is None]
    if unanswered:
        raise HTTPException(status_code=400, detail="All questions must be answered before completing the interview.")

    # Build LLM prompt
    qa_pairs = [
        {
            "question_id": str(q.id),
            "question": q.question_text,
            "answer": q.answer_text
        }
        for q in questions
    ]
    prompt = {
        "system_prompt": (
            "You are an expert technical interviewer. Evaluate the following interview session. "
            "For each question, provide a score (0-1) and brief feedback. Then, summarize the "
            "candidate's strengths and weaknesses and provide an overall confidence score (0-1). "
            "Always respond with valid JSON only."
        ),
        "user_prompt": (
            f"Session Q&A: {qa_pairs}\n"
            "OUTPUT FORMAT (JSON): "
            '{"summary": "<string>", "confidence_score": <float>, '
            '"questions_feedback": [{"question_id": "<string>", "evaluation_score": <float>, '
            '"feedback_comment": "<string>"}]}'
        ),
    }

    llm_provider = get_llm_provider()
    try:
        llm_response = llm_provider.generate_feedback(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM evaluation failed: {e}")

    # Parse and persist feedback
    summary = llm_response.get("summary")
    confidence_score = llm_response.get("confidence_score")
    questions_feedback = llm_response.get("questions_feedback", [])
    if summary is None or confidence_score is None or not questions_feedback:
        raise HTTPException(status_code=500, detail="LLM response missing required fields.")

    # Update session
    session.completed_at = datetime.now(timezone.utc)  # type: ignore
    session.final_score = confidence_score
    session.feedback_summary = summary
    db.commit()

    # Update question feedback
    for feedback in questions_feedback:
        qid = feedback.get("question_id")
        q = next((q for q in questions if str(q.id) == str(qid)), None)
        if q:
            q.evaluation_score = feedback.get("evaluation_score")
            q.feedback_comment = feedback.get("feedback_comment")
    db.commit()

    # Build response
    return SummaryOut(
        session_id=session.id,  #type:ignore
        final_score=confidence_score,
        feedback_summary=summary,
        question_feedback=[
            QuestionFeedback(
                question_id=UUID(qf["question_id"]),
                evaluation_score=qf["evaluation_score"],
                feedback_comment=qf["feedback_comment"]
            ) for qf in questions_feedback
        ]
    )

def get_interview_summary(db: Session, session):
    # Fetch all questions for the session
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this session.")

    # Build Q&A list
    qa_list = [
        {
            "question_id": str(q.id),
            "question": q.question_text,
            "answer": q.answer_text,
            "evaluation_score": q.evaluation_score,
            "feedback_comment": q.feedback_comment
        }
        for q in questions
    ]

    # Fetch user full name
    user = db.query(User).filter(User.id == session.user_id).first()
    user_full_name = getattr(user, "full_name", None) if user else None

    # Compose summary
    summary = {
        "session_id": str(session.id),
        "user_full_name": user_full_name,
        "resume_id": str(session.resume_id),
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        "final_score": session.final_score,
        "feedback_summary": session.feedback_summary,
        "questions": qa_list,
    }

    # Add strengths/weaknesses if available
    if session.feedback_summary:
        summary["strengths_weaknesses"] = session.feedback_summary
    else:
        summary["strengths_weaknesses"] = "Not available. Complete the interview to get feedback."

    return summary
