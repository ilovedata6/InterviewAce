"""
Interview use cases — application-specific business rules for interview sessions.

Each use case orchestrates domain logic through repository interfaces,
the LLM provider interface, and domain entities.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from app.application.dto.interview import (
    InterviewSummaryResult,
    QuestionResult,
    StartInterviewInput,
    SubmitAnswerInput,
)
from app.domain.entities.interview import (
    InterviewQuestionEntity,
    InterviewSessionEntity,
)
from app.domain.exceptions import (
    EntityNotFoundError,
    InterviewError,
)
from app.domain.interfaces.llm_provider import ILLMProvider
from app.domain.interfaces.repositories import (
    IInterviewRepository,
    IResumeRepository,
    IUserRepository,
)

logger = structlog.get_logger(__name__)


# ── Helpers ─────────────────────────────────────────────────────────────────


async def _get_owned_session(
    repo: IInterviewRepository,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
) -> InterviewSessionEntity:
    """Fetch a session and verify ownership.  Raises on failure."""
    session = await repo.get_session_by_id(session_id)
    if session is None or session.user_id != user_id:
        raise EntityNotFoundError("InterviewSession", str(session_id))
    return session


# ── Start Interview ─────────────────────────────────────────────────────────


class StartInterviewUseCase:
    """Create a new interview session and generate AI questions."""

    def __init__(
        self,
        interview_repo: IInterviewRepository,
        resume_repo: IResumeRepository,
        llm_provider: ILLMProvider,
    ) -> None:
        self._interview_repo = interview_repo
        self._resume_repo = resume_repo
        self._llm_provider = llm_provider

    async def execute(self, dto: StartInterviewInput) -> InterviewSessionEntity:
        # 1. Get specified resume or latest
        if dto.resume_id:
            resume = await self._resume_repo.get_by_id(dto.resume_id)
            if not resume or resume.user_id != dto.user_id:
                raise EntityNotFoundError("Resume", str(dto.resume_id))
        else:
            resume = await self._resume_repo.get_latest_by_user_id(dto.user_id)
        if not resume:
            raise EntityNotFoundError("Resume")

        # 2. Create session entity with config
        session_entity = InterviewSessionEntity(
            user_id=dto.user_id,
            resume_id=resume.id,
            started_at=datetime.now(UTC),
            difficulty=dto.difficulty,
            question_count=dto.question_count,
            focus_areas=dto.focus_areas,
        )
        saved_session = await self._interview_repo.create_session(session_entity)

        # 3. Build resume context & generate questions via LLM
        #    Run the synchronous/blocking LLM call in a thread so we
        #    don't freeze the async event loop.
        resume_context = self._build_resume_context(resume)
        prompt = self._build_prompt(
            resume_context,
            question_count=dto.question_count,
            difficulty=dto.difficulty,
            focus_areas=dto.focus_areas,
        )
        try:
            raw_questions = await asyncio.to_thread(
                self._llm_provider.generate_questions, prompt
            )
            logger.info(
                "questions_generated",
                session_id=str(saved_session.id),
                count=len(raw_questions),
            )
        except Exception as e:
            logger.error("llm_call_failed", session_id=str(saved_session.id), error=str(e))
            raise InterviewError("Failed to generate questions") from e

        # 4. Persist questions with metadata (batch — single transaction)
        q_entities: list[InterviewQuestionEntity] = []
        for idx, q_data in enumerate(raw_questions):
            # Support both dict (with metadata) and plain string from LLM
            if isinstance(q_data, dict):
                q_text = q_data.get("question", str(q_data))
                q_category = q_data.get("type", "general")
                q_difficulty = q_data.get(
                    "difficulty", dto.difficulty if dto.difficulty != "mixed" else "medium"
                )
            else:
                q_text = str(q_data)
                q_category = "general"
                q_difficulty = dto.difficulty if dto.difficulty != "mixed" else "medium"

            q_entities.append(
                InterviewQuestionEntity(
                    session_id=saved_session.id,
                    question_text=q_text,
                    category=q_category,
                    difficulty=q_difficulty,
                    order_index=idx,
                )
            )

        await self._interview_repo.add_questions_batch(q_entities)

        # Return the session (with questions attached)
        return await self._interview_repo.get_session_by_id(saved_session.id)  # type: ignore

    # ── Private helpers ────────────────────────────────────────────────

    @staticmethod
    def _build_resume_context(resume) -> dict:
        experience = (resume.analysis or {}).get("experience", [])
        projects = [
            {"description": exp.get("description", "No description available")}
            for exp in experience
        ]
        return {
            "inferred_role": resume.inferred_role,
            "years_of_experience": resume.years_of_experience,
            "skills": resume.skills,
            "projects": projects,
        }

    @staticmethod
    def _build_prompt(
        ctx: dict,
        *,
        question_count: int = 12,
        difficulty: str = "mixed",
        focus_areas: list[str] | None = None,
    ) -> dict:
        skills = ctx.get("skills") or []
        if not isinstance(skills, list):
            skills = []
        projects = (ctx.get("projects") or [])[:4]
        project_details = "\n".join(f"  - {p['description']}" for p in projects)

        difficulty_instruction = ""
        if difficulty == "mixed":
            difficulty_instruction = (
                "Use a mix of easy, medium, and hard questions. "
                "Distribute roughly: 30% easy, 40% medium, 30% hard.\n"
            )
        else:
            difficulty_instruction = (
                f"All questions should be at **{difficulty}** difficulty level.\n"
            )

        focus_instruction = ""
        if focus_areas:
            focus_instruction = f"Focus the questions on these areas: {', '.join(focus_areas)}.\n"

        system_prompt = (
            "You are an expert technical interviewer conducting a real interview. "
            "Generate precise, focused interview questions that test a candidate's "
            "actual skills and experience. Always respond with valid JSON only."
        )
        user_prompt = (
            f"Candidate Profile:\n"
            f"- Target Role: {ctx.get('inferred_role') or 'Software Engineer'}\n"
            f"- Years of Experience: {ctx.get('years_of_experience') or 'Unknown'}\n"
            f"- Key Skills: {', '.join(skills[:15]) if skills else 'Not specified'}\n"
        )
        if project_details:
            user_prompt += f"- Notable Projects:\n{project_details}\n"

        user_prompt += (
            f"\n{difficulty_instruction}"
            f"{focus_instruction}"
            "\nQUESTION GUIDELINES:\n"
            "- Keep questions concise and direct (1-2 sentences max).\n"
            "- Only scenario-based or system_design questions may be longer (up to 3-4 sentences) "
            "to set up proper context.\n"
            "- Ask about specific technologies from the candidate's skill set.\n"
            "- Include questions referencing their actual project experience.\n"
            "- Avoid generic filler questions — every question should be purposeful.\n"
            "- Mix question types: technical, behavioral, project-based, system_design, and coding.\n"
            "\nOUTPUT FORMAT:\n"
            "Return a JSON object with a \"questions\" array. Each element:\n"
            '  { "type": "technical|behavioral|project|system_design|coding", '
            '"question": "<concise question text>", "difficulty": "easy|medium|hard" }\n'
            f"\nTotal questions: {question_count}\n"
            "No additional text, no markdown, no code fences — ONLY the JSON object."
        )
        return {"system_prompt": system_prompt, "user_prompt": user_prompt}


# ── Submit Answer ───────────────────────────────────────────────────────────


class SubmitAnswerUseCase:
    """Submit an answer and return the next unanswered question (or None)."""

    def __init__(self, interview_repo: IInterviewRepository) -> None:
        self._interview_repo = interview_repo

    async def execute(self, dto: SubmitAnswerInput) -> QuestionResult | None:
        _session = await _get_owned_session(self._interview_repo, dto.user_id, dto.session_id)

        # Find the question
        question = await self._interview_repo.get_question_by_id(dto.question_id, dto.session_id)
        if not question:
            raise EntityNotFoundError("InterviewQuestion", str(dto.question_id))

        # Record answer
        question.answer_text = dto.answer_text
        if dto.time_taken_seconds is not None:
            question.time_taken_seconds = dto.time_taken_seconds
        await self._interview_repo.update_question(question)

        # Return next unanswered
        next_q = await self._interview_repo.get_next_unanswered_question(dto.session_id)
        if not next_q:
            return None
        return QuestionResult(
            question_id=next_q.id,
            question_text=next_q.question_text,
            category=next_q.category,
            difficulty=next_q.difficulty,
            order_index=next_q.order_index,
        )


# ── Get Next Question ───────────────────────────────────────────────────────


class GetNextQuestionUseCase:
    """Get the next unanswered question for a session."""

    def __init__(self, interview_repo: IInterviewRepository) -> None:
        self._interview_repo = interview_repo

    async def execute(self, user_id: uuid.UUID, session_id: uuid.UUID) -> QuestionResult | None:
        await _get_owned_session(self._interview_repo, user_id, session_id)

        next_q = await self._interview_repo.get_next_unanswered_question(session_id)
        if not next_q:
            return None
        return QuestionResult(
            question_id=next_q.id,
            question_text=next_q.question_text,
            category=next_q.category,
            difficulty=next_q.difficulty,
            order_index=next_q.order_index,
        )


# ── Complete Interview ──────────────────────────────────────────────────────


class CompleteInterviewUseCase:
    """Evaluate all answers and finalize the interview session."""

    def __init__(
        self,
        interview_repo: IInterviewRepository,
        llm_provider: ILLMProvider,
    ) -> None:
        self._interview_repo = interview_repo
        self._llm_provider = llm_provider

    async def execute(self, user_id: uuid.UUID, session_id: uuid.UUID) -> InterviewSummaryResult:
        session = await _get_owned_session(self._interview_repo, user_id, session_id)

        questions = await self._interview_repo.get_questions_by_session_id(session_id)
        if not questions:
            raise InterviewError("No questions found for this session.")

        unanswered = [q for q in questions if not q.is_answered()]
        if unanswered:
            raise InterviewError("All questions must be answered before completing the interview.")

        # Build LLM prompt
        qa_pairs = [
            {
                "question_id": str(q.id),
                "question": q.question_text,
                "answer": q.answer_text,
                "category": q.category,
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
                '"strengths": ["<string>", ...], '
                '"weaknesses": ["<string>", ...], '
                '"score_breakdown": {"technical": <float>, "behavioral": <float>, '
                '"project": <float>, "overall": <float>}, '
                '"questions_feedback": [{"question_id": "<string>", "evaluation_score": <float>, '
                '"feedback_comment": "<string>"}]}'
            ),
        }

        try:
            llm_response = await asyncio.to_thread(
                self._llm_provider.generate_feedback, prompt
            )
        except Exception as e:
            raise InterviewError(f"LLM evaluation failed: {e}") from e

        summary = llm_response.get("summary")
        confidence_score = llm_response.get("confidence_score")
        questions_feedback = llm_response.get("questions_feedback", [])
        strengths = llm_response.get("strengths")
        weaknesses = llm_response.get("weaknesses")
        score_breakdown = llm_response.get("score_breakdown")

        if summary is None or confidence_score is None or not questions_feedback:
            raise InterviewError("LLM response missing required fields.")

        # Update session
        session.complete(score=confidence_score, summary=summary, score_breakdown=score_breakdown)
        await self._interview_repo.update_session(session)

        # Update question feedback
        for fb in questions_feedback:
            qid = fb.get("question_id")
            matched = next((q for q in questions if str(q.id) == str(qid)), None)
            if matched:
                matched.evaluation_score = fb.get("evaluation_score")
                matched.feedback_comment = fb.get("feedback_comment")
                await self._interview_repo.update_question(matched)

        return InterviewSummaryResult(
            session_id=session.id,
            final_score=confidence_score,
            feedback_summary=summary,
            question_feedback=questions_feedback,
            score_breakdown=score_breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
        )


# ── Get Session ─────────────────────────────────────────────────────────────


class GetSessionUseCase:
    """Retrieve a specific interview session for the user."""

    def __init__(self, interview_repo: IInterviewRepository) -> None:
        self._interview_repo = interview_repo

    async def execute(self, user_id: uuid.UUID, session_id: uuid.UUID) -> InterviewSessionEntity:
        return await _get_owned_session(self._interview_repo, user_id, session_id)


# ── Get History ─────────────────────────────────────────────────────────────


class GetHistoryUseCase:
    """List interview sessions with pagination."""

    def __init__(self, interview_repo: IInterviewRepository) -> None:
        self._interview_repo = interview_repo

    async def execute(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[InterviewSessionEntity], int]:
        sessions = await self._interview_repo.get_sessions_by_user_id(
            user_id, skip=skip, limit=limit
        )
        total = await self._interview_repo.count_sessions_by_user_id(user_id)
        return sessions, total


# ── Get Summary ─────────────────────────────────────────────────────────────


class GetSummaryUseCase:
    """Retrieve the detailed summary for a completed interview."""

    def __init__(
        self,
        interview_repo: IInterviewRepository,
        user_repo: IUserRepository,
    ) -> None:
        self._interview_repo = interview_repo
        self._user_repo = user_repo

    async def execute(self, user_id: uuid.UUID, session_id: uuid.UUID) -> dict[str, Any]:
        session = await _get_owned_session(self._interview_repo, user_id, session_id)

        questions = await self._interview_repo.get_questions_by_session_id(session_id)
        if not questions:
            raise EntityNotFoundError("InterviewQuestion")

        qa_list = [
            {
                "question_id": str(q.id),
                "question": q.question_text,
                "answer": q.answer_text,
                "evaluation_score": q.evaluation_score,
                "feedback_comment": q.feedback_comment,
            }
            for q in questions
        ]

        # User full name
        user = await self._user_repo.get_by_id(user_id)
        user_full_name = user.full_name if user else None

        result: dict[str, Any] = {
            "session_id": str(session.id),
            "user_full_name": user_full_name,
            "resume_id": str(session.resume_id),
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "final_score": session.final_score,
            "feedback_summary": session.feedback_summary,
            "questions": qa_list,
        }

        if session.feedback_summary:
            result["strengths_weaknesses"] = session.feedback_summary
        else:
            result["strengths_weaknesses"] = (
                "Not available. Complete the interview to get feedback."
            )

        return result
