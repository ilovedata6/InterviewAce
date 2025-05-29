from fastapi import APIRouter
from .start import router as interview_session_router

router = APIRouter()

router.include_router(interview_session_router, prefix="/start", tags=["interview-session-start"])
