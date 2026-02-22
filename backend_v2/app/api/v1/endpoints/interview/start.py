from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user, get_start_interview_uc
from app.models.user import User
from app.schemas.interview import InterviewSessionInDB
from app.application.use_cases.interview import StartInterviewUseCase
from app.domain.exceptions import EntityNotFoundError, InterviewError

router = APIRouter()

@router.post(
    "",
    response_model=InterviewSessionInDB,
    summary="Start an interview session",
    response_description="The newly created interview session with generated questions.",
)
async def start_interview_session(
    current_user: User = Depends(get_current_user),
    use_case: StartInterviewUseCase = Depends(get_start_interview_uc),
):
    """Create a new interview session linked to the user's latest resume.

    Generates 12-15 AI-powered questions (technical, behavioral, project-based).

    Raises:
        404: No resume found — upload one first.
        500: Question generation failed.
    """
    try:
        session = await use_case.execute(current_user.id)
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first.",
        )
    except InterviewError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate questions",
        )
    return session
