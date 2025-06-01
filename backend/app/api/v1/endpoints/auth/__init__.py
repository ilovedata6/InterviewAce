from fastapi import APIRouter
from .register import router as register_router
from .login import router as login_router
from .logout import router as logout_router
from .me import router as me_router
from .refresh import router as refresh_router
from .change_password import router as change_password_router
from .reset_password_request import router as reset_password_request_router
from .reset_password_confirm import router as reset_password_confirm_router

router = APIRouter()

router.include_router(register_router, tags=["register"])
router.include_router(login_router, tags=["login"])
router.include_router(logout_router, tags=["logout"])
router.include_router(me_router, tags=["me"])
router.include_router(refresh_router, tags=["refresh"])
router.include_router(change_password_router, tags=["change-password"])
router.include_router(reset_password_request_router)
router.include_router(reset_password_confirm_router)