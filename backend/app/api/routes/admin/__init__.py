from fastapi import APIRouter

from app.api.routes.admin.countries import router as admin_countries_router
from app.api.routes.admin.users import router as admin_users_router

router = APIRouter()
router.include_router(admin_countries_router, prefix="/countries")
router.include_router(admin_users_router, prefix="/users")