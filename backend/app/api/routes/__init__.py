from fastapi import APIRouter

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.individual import router as individual_router


router = APIRouter()

router.include_router(admin_router, prefix="/admin")
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(individual_router, prefix="/individual")
