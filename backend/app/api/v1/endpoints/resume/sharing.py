from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import generate_share_token
from app.db.session import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeResponse, ResumeShareRequest, ResumeShareResponse

router = APIRouter()


@router.post("/{resume_id}/share", response_model=ResumeShareResponse)
async def share_resume(
    resume_id: str,
    share_request: ResumeShareRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Share a resume with others."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    # Generate share token
    share_token = generate_share_token()

    # Calculate expiry date if specified
    expiry_date = None
    if share_request.expiry_days:
        expiry_date = datetime.utcnow() + timedelta(days=share_request.expiry_days)

    # Update resume sharing settings
    resume.is_public = share_request.is_public
    resume.share_token = share_token
    await db.commit()

    # Generate share URL
    share_url = f"{settings.FRONTEND_URL}/resume/shared/{share_token}"

    return ResumeShareResponse(
        share_token=share_token,
        share_url=share_url,
        expiry_date=expiry_date,
        is_public=share_request.is_public,
    )


@router.get("/shared/{share_token}", response_model=ResumeResponse)
async def get_shared_resume(share_token: str, db: AsyncSession = Depends(get_db)):
    """Get a shared resume using the share token."""
    result = await db.execute(select(Resume).where(Resume.share_token == share_token))
    resume = result.scalars().first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared resume not found")

    if not resume.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This resume is not publicly shared"
        )

    return resume


@router.post("/{resume_id}/unshare", status_code=status.HTTP_204_NO_CONTENT)
async def unshare_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove sharing settings from a resume."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    # Remove sharing settings
    resume.is_public = False
    resume.share_token = None
    await db.commit()


@router.get("/{resume_id}/share-status", response_model=ResumeShareResponse)
async def get_share_status(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current sharing status of a resume."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    share_url = None
    if resume.share_token:
        share_url = f"{settings.FRONTEND_URL}/resume/shared/{resume.share_token}"

    return ResumeShareResponse(
        share_token=resume.share_token,
        share_url=share_url,
        expiry_date=None,  # We don't store expiry date in the database
        is_public=resume.is_public,
    )
