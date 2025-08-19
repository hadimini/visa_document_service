from fastapi import APIRouter

from app.api.routes.admin import router as admin_router
from app.api.routes.users import router as users_router


router = APIRouter()

router.include_router(admin_router, prefix="/admin", tags=["admins"])
router.include_router(users_router, prefix="/user", tags=["users"])
