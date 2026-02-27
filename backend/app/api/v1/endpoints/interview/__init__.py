from fastapi import APIRouter

from .answer import router as answer_router
from .complete import router as complete_router
from .history import router as history_router
from .next_question import router as next_question_router
from .session import router as session_router
from .start import router as interview_session_router
from .summary import router as summary_router

router = APIRouter()

router.include_router(interview_session_router, prefix="/start", tags=["interview-session-start"])
router.include_router(next_question_router, tags=["interview-question"])
router.include_router(answer_router, tags=["interview-answer"])
router.include_router(complete_router, tags=["interview-complete"])
router.include_router(summary_router, tags=["interview-summary"])
router.include_router(history_router, tags=["interview-history"])
router.include_router(session_router, tags=["interview-session"])
