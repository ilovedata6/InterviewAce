from fastapi import APIRouter
from app.api.v1.endpoints import interview, resume
from app.api.v1.endpoints import auth
from app.api.v1.endpoints.tasks import router as tasks_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
api_router.include_router(tasks_router, tags=["tasks"])