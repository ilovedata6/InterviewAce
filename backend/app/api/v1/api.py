from fastapi import APIRouter
from app.api.v1.endpoints import auth, interview
from app.api.v1.endpoints.resume import router as resume_router

api_router = APIRouter()
 
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"]) 
api_router.include_router(resume_router, prefix="/resume", tags=["resume"]) 