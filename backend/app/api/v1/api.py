from fastapi import APIRouter
from app.api.v1.endpoints import auth, interview, resume

api_router = APIRouter()
 
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"]) 
api_router.include_router(resume.router, prefix="/resume", tags=["resume"]) 