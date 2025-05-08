from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ResumeStatus(str, Enum):
    PENDING = "pending"
    ANALYZED = "analyzed"
    ERROR = "error"

class ResumeBase(BaseModel):
    title: str = Field(..., description="Title of the resume")
    description: Optional[str] = Field(None, description="Optional description of the resume")

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(ResumeBase):
    title: Optional[str] = None
    description: Optional[str] = None

class ResumeInDB(ResumeBase):
    id: int
    user_id: int
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    status: ResumeStatus
    created_at: datetime
    updated_at: datetime
    analysis: Optional[dict] = None

    class Config:
        from_attributes = True

class ResumeResponse(ResumeInDB):
    pass

class ResumeList(BaseModel):
    resumes: List[ResumeResponse]
    total: int

class ResumeAnalysis(BaseModel):
    skills: List[str] = Field(..., description="List of skills extracted from resume")
    experience: List[dict] = Field(..., description="List of work experiences")
    education: List[dict] = Field(..., description="List of educational qualifications")
    summary: str = Field(..., description="Summary of the resume content")
    recommendations: List[str] = Field(..., description="List of improvement recommendations")

class ResumeUploadResponse(BaseModel):
    id: int
    file_name: str
    status: ResumeStatus
    message: str

class ResumeAnalysisResponse(BaseModel):
    resume_id: int
    analysis: ResumeAnalysis
    status: ResumeStatus
    created_at: datetime 