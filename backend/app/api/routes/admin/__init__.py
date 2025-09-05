from fastapi import APIRouter, Depends

from app.api.dependencies.auth import role_required
from app.api.routes.admin.clients import router as client_router
from app.api.routes.admin.countries import router as countries_router
from app.api.routes.admin.services import router as services_router
from app.api.routes.admin.urgencies import router as urgencies_router
from app.api.routes.admin.users import router as users_router
from app.api.routes.admin.visa_types import router as visa_types_router
from app.models.users import User

router = APIRouter()

router.include_router(
    router=client_router,
    dependencies=[
        Depends(role_required(User.ROLE_ADMIN))
    ],
    prefix="/clients",
    tags=["admin-clients"]
)

router.include_router(
    router=countries_router,
    dependencies=[
        Depends(role_required(User.ROLE_ADMIN))
    ],
    prefix="/countries",
    tags=["admin-countries"]
)

router.include_router(
    router=services_router,
    dependencies=[
        Depends(role_required(User.ROLE_ADMIN))
    ],
    prefix="/services",
    tags=["admin-services"]
)

router.include_router(
    router=users_router,
    dependencies=[
        Depends(role_required(User.ROLE_ADMIN))
    ],
    prefix="/users",
    tags=["admin-users"]
)

router.include_router(
    router=urgencies_router,
    dependencies=[
        Depends(role_required(User.ROLE_ADMIN))
    ],
    prefix="/urgencies",
    tags=["admin-urgencies"]
)

router.include_router(
    router=visa_types_router,
    dependencies=[
        Depends(role_required(User.ROLE_ADMIN))
    ],
    prefix="/visa_types",
    tags=["admin-visa_types"]
)
