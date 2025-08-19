from fastapi import APIRouter

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router


router = APIRouter()

router.include_router(admin_router, prefix="/admin", tags=["admins"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
