from fastapi import APIRouter
from .start import router as interview_session_router
from .next_question import router as next_question_router
from .answer import router as answer_router
from .complete import router as complete_router
from .summary import router as summary_router

router = APIRouter()

router.include_router(interview_session_router, prefix="/start", tags=["interview-session-start"])
router.include_router(next_question_router, tags=["interview-question"])
router.include_router(answer_router, tags=["interview-answer"])
router.include_router(complete_router, tags=["interview-complete"])
router.include_router(summary_router, tags=["interview-summary"])
