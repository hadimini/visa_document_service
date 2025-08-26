from fastapi import APIRouter, Depends

from app.api.dependencies.auth import role_required
from app.api.routes.individual.countries import router as individual_countries_router
from app.models.users import User


router = APIRouter()

router.include_router(
    router=individual_countries_router,
    dependencies=[
        Depends(role_required(User.ROLE_INDIVIDUAL))
    ],
    prefix="/countries",
    tags=["individual-countries"]
)
