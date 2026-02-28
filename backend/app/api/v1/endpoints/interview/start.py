from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_start_interview_uc
from app.application.dto.interview import StartInterviewInput
from app.application.use_cases.interview import StartInterviewUseCase
from app.domain.exceptions import EntityNotFoundError, InterviewError
from app.models.user import User
from app.schemas.interview import InterviewSessionInDB, InterviewStartRequest

router = APIRouter()


@router.post(
    "",
    response_model=InterviewSessionInDB,
    summary="Start an interview session",
    response_description="The newly created interview session with generated questions.",
)
async def start_interview_session(
    body: InterviewStartRequest = None,
    current_user: User = Depends(get_current_user),
    use_case: StartInterviewUseCase = Depends(get_start_interview_uc),
):
    """Create a new interview session linked to the user's resume.

    Accepts optional configuration:
    - **resume_id**: specific resume to use (default: latest)
    - **question_count**: 5–30 (default: 12)
    - **difficulty**: easy | medium | hard | mixed (default: mixed)
    - **focus_areas**: list of focus topics (optional)

    Raises:
        404: No resume found — upload one first.
        500: Question generation failed.
    """
    if body is None:
        body = InterviewStartRequest()

    dto = StartInterviewInput(
        user_id=current_user.id,
        resume_id=body.resume_id,
        question_count=body.question_count,
        difficulty=body.difficulty,
        focus_areas=body.focus_areas,
    )

    try:
        session = await use_case.execute(dto)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first.",
        ) from e
    except InterviewError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AI question generation temporarily unavailable. "
                "Please try again in a few seconds."
            ),
        ) from e
    return session
