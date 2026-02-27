from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Import enums from domain layer — single source of truth
from app.domain.value_objects.enums import FileType, ResumeStatus


class Experience(BaseModel):
    company: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=100)
    start_date: datetime
    end_date: datetime | None = None
    description: str = Field(..., min_length=10)
    location: str | None = Field(None, max_length=100)
    is_current: bool = False

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v, info):
        if v and "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class Education(BaseModel):
    institution: str = Field(..., min_length=1, max_length=100)
    degree: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=100)
    start_date: datetime
    end_date: datetime | None = None
    gpa: float | None = Field(None, ge=0.0, le=4.0)
    is_current: bool = False

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v, info):
        if v and "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class ResumeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title of the resume")
    description: str | None = Field(
        None, max_length=500, description="Optional description of the resume"
    )
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def tags_max_length(cls, v):
        if len(v) > 10:
            raise ValueError("No more than 10 tags are allowed")
        return v


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(ResumeBase):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    tags: list[str] | None = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    skills: list[str] = Field(..., description="List of skills extracted from resume")
    experience: list[Experience] = Field(..., description="List of work experiences")
    education: list[Education] = Field(..., description="List of educational qualifications")
    summary: str = Field(
        ..., min_length=50, max_length=1000, description="Summary of the resume content"
    )
    recommendations: list[str] = Field(..., description="List of improvement recommendations")
    job_titles: list[str] = Field(..., description="List of potential job titles")
    years_of_experience: float = Field(..., ge=0, description="Total years of experience")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score of the analysis")


class ResumeInDB(ResumeBase):
    id: UUID | str
    user_id: UUID | str
    file_path: str
    file_name: str
    file_size: int
    file_type: FileType
    status: ResumeStatus
    inferred_role: str | None = None
    years_of_experience: float | None = None
    skills: list[str] = Field(
        default_factory=list, description="List of skills extracted from the resume"
    )
    created_at: datetime
    updated_at: datetime
    analysis: dict[str, Any] | None = None
    version: int = Field(default=1, ge=1)
    parent_version_id: UUID | str | None = None
    is_public: bool = False
    share_token: str | None = None

    class Config:
        from_attributes = True


class ResumeResponse(ResumeInDB):
    pass


class ResumeList(BaseModel):
    resumes: list[ResumeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ResumeUploadResponse(BaseModel):
    id: str
    file_name: str
    status: ResumeStatus
    message: str
    file_size: int
    file_type: FileType
    task_id: str | None = None


class ResumeAnalysisResponse(BaseModel):
    resume_id: str
    analysis: dict[str, Any] | None = None
    status: ResumeStatus
    created_at: datetime
    processing_time: float | None = None
    confidence_score: float | None = None


class ResumeShareRequest(BaseModel):
    is_public: bool = False
    expiry_days: int | None = Field(None, ge=1, le=30)
    allowed_emails: list[str] | None = Field(None)

    @field_validator("allowed_emails")
    @classmethod
    def allowed_emails_max_length(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError("No more than 10 allowed emails are permitted")
        return v


class ResumeShareResponse(BaseModel):
    share_token: str
    share_url: str
    expiry_date: datetime | None
    is_public: bool


class ResumeVersion(BaseModel):
    version: int
    created_at: datetime
    changes: list[str]
    parent_version_id: str | None


class ResumeVersionList(BaseModel):
    versions: list[ResumeVersion]
    current_version: int
