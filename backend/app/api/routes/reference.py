from fastapi import Depends, APIRouter

from app.api.dependencies.db import get_repository
from app.api.routes.base.urgencies import urgency_list
from app.database.repositories.countries import CountriesRepository
from app.schemas.country import CountryFilterSchema, CountryReferencePublicSchema
from app.schemas.urgencies import UrgencyPublicSchema

router = APIRouter()


@router.get(
    path="/countries",
    response_model=list[CountryReferencePublicSchema],
    status_code=200,
    summary="Get all countries - unpaginated",
    name="reference:country-list"
)
async def country_list(
        filters: CountryFilterSchema = Depends(),
        countries_repo: CountriesRepository = Depends(get_repository(CountriesRepository))
):
    results = await countries_repo.get_full_list(filters=filters)
    return results


urgency_list = router.get(
    path="/urgencies",
    response_model=list[UrgencyPublicSchema],
    status_code=200,
    summary="Get all urgencies - unpaginated",
    name="reference:urgency-list"
)(urgency_list)
