from fastapi import APIRouter
from .register import router as register_router
from .login import router as login_router
from .logout import router as logout_router

router = APIRouter()

router.include_router(register_router, tags=["register"])
router.include_router(login_router, tags=["login"])
router.include_router(logout_router, tags=["logout"])