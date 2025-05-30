from fastapi import APIRouter
from .start import router as interview_session_router
from .next_question import router as next_question_router
from .answer import router as answer_router


router = APIRouter()

router.include_router(interview_session_router, prefix="/start", tags=["interview-session-start"])
router.include_router(next_question_router, tags=["interview-question"])
router.include_router(answer_router, tags=["interview-answer"])