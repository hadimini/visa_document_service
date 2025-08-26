from fastapi import APIRouter, Depends

from app.api.dependencies.auth import role_required
from app.api.routes.admin.countries import router as admin_countries_router
from app.api.routes.admin.users import router as admin_users_router
from app.models.users import User

router = APIRouter()

router.include_router(
    router=admin_countries_router,
    dependencies=[
        Depends(role_required(User.ROLE_ADMIN))
    ],
    prefix="/countries",
    tags=["admin-countries"]
)

router.include_router(
    router=admin_users_router,
    dependencies=[
        Depends(role_required(User.ROLE_ADMIN))
    ],
    prefix="/users",
    tags=["admin-users"]
)
