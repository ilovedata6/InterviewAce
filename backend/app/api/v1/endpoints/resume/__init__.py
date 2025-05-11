from fastapi import APIRouter
from .upload import router as upload_router
from .analysis import router as analysis_router
from .management import router as management_router
from .sharing import router as sharing_router
from .export import router as export_router
from .version import router as version_router

router = APIRouter()

router.include_router(upload_router, prefix="/upload", tags=["resume-upload"])
router.include_router(analysis_router, prefix="/analysis", tags=["resume-analysis"])
router.include_router(management_router, prefix="/management", tags=["resume-management"])
router.include_router(sharing_router, prefix="/sharing", tags=["resume-sharing"])
router.include_router(export_router, prefix="/export", tags=["resume-export"])
router.include_router(version_router, prefix="/version", tags=["resume-version"]) 