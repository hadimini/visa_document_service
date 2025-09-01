from fastapi import APIRouter, Depends

from app.api.dependencies.auth import login_required
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.reference import router as references_router


router = APIRouter()

router.include_router(admin_router, prefix="/admin")
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(
    references_router,
    prefix="/reference",
    tags=["reference"],
    dependencies=[Depends(login_required)]
)
