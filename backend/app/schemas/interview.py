from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class InterviewQuestionBase(BaseModel):
    question_text: str
    answer_text: Optional[str] = None
    evaluation_score: Optional[float] = None
    feedback_comment: Optional[str] = None

class InterviewQuestionCreate(InterviewQuestionBase):
    session_id: UUID

class InterviewQuestionInDB(InterviewQuestionBase):
    id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InterviewSessionBase(BaseModel):
    user_id: UUID
    resume_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    final_score: Optional[float] = None
    feedback_summary: Optional[str] = None

class InterviewSessionCreate(BaseModel):
    resume_id: UUID

class InterviewSessionInDB(BaseModel):
    id: UUID
    user_id: UUID
    resume_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    final_score: Optional[float] = None
    feedback_summary: Optional[str] = None

    class Config:
        orm_mode = True

class QuestionOut(BaseModel):
    question_id: UUID
    question_text: str