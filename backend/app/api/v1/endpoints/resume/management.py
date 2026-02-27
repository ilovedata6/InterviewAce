from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import (
    get_current_user,
    get_delete_resume_uc,
    get_get_resume_uc,
    get_list_resumes_uc,
    get_update_resume_uc,
)
from app.application.dto.resume import ResumeListInput, ResumeUpdateInput
from app.application.use_cases.resume import (
    DeleteResumeUseCase,
    GetResumeUseCase,
    ListResumesUseCase,
    UpdateResumeUseCase,
)
from app.domain.exceptions import EntityNotFoundError
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.resume import ResumeResponse, ResumeStatus, ResumeUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[ResumeResponse],
    summary="List resumes",
    response_description="Paginated list of resumes owned by the authenticated user.",
)
async def list_resumes(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return"),
    status_filter: ResumeStatus | None = Query(None, alias="status"),
    search: str | None = None,
    use_case: ListResumesUseCase = Depends(get_list_resumes_uc),
):
    """List all resumes for the current user with pagination and optional filtering.

    Filter by `status` (PENDING, COMPLETED, FAILED) or full-text `search` on title/description.
    """
    items, total = await use_case.execute(
        ResumeListInput(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status_filter=status_filter.value if status_filter else None,
            search=search,
        )
    )
    return PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Get a resume",
    response_description="Resume details.",
)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    use_case: GetResumeUseCase = Depends(get_get_resume_uc),
):
    """Get a specific resume by ID.

    Raises:
        404: Resume not found or not owned by the user.
    """
    try:
        return await use_case.execute(current_user.id, UUID(resume_id))
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        ) from e


@router.put(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Update resume metadata",
    response_description="Updated resume details.",
)
async def update_resume(
    resume_id: str,
    resume_update: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    use_case: UpdateResumeUseCase = Depends(get_update_resume_uc),
):
    """Update resume metadata (title, description).

    Raises:
        404: Resume not found or not owned by the user.
    """
    update_data = resume_update.dict(exclude_unset=True)
    try:
        return await use_case.execute(
            ResumeUpdateInput(
                user_id=current_user.id,
                resume_id=UUID(resume_id),
                title=update_data.get("title"),
                description=update_data.get("description"),
            )
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        ) from e


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resume",
    response_description="No content.",
)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    use_case: DeleteResumeUseCase = Depends(get_delete_resume_uc),
):
    """Delete a resume and its associated file from disk.

    Raises:
        404: Resume not found or not owned by the user.
    """
    try:
        await use_case.execute(current_user.id, UUID(resume_id))
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        ) from e
