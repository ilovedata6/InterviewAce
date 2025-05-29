import logging
from typing import List, cast
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.interview import InterviewSession, InterviewQuestion
from app.schemas.interview import InterviewQuestionCreate
from app.db.session import get_db
from app.core.config import settings
from app.utils.llm_client import LLMClient
from app.models.resume import Resume  # Assuming Resume model is in app.models.resume
from app.models.user import User
from fastapi import HTTPException, status

import os 
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class InterviewOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.llm_client = LLMClient(api_key=api_key)

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
            questions = self.llm_client.generate_questions(prompt)
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
                "that test a candidate’s skills, Professional experience, and past projects."
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
