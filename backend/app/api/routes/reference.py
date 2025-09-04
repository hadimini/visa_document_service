from fastapi import Depends, APIRouter

from app.api.dependencies.db import get_repository
from app.api.routes.base.urgencies import urgency_list
from app.database.repositories.countries import CountriesRepository
from app.database.repositories.country_visas import CountryVisasRepository
from app.schemas.country import CountryFilterSchema, CountryReferencePublicSchema
from app.schemas.country_visa import CountryVisaReferencePublicSchema
from app.schemas.urgency import UrgencyPublicSchema

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


@router.get(
    path="/countries/{country_id}/visa_types",
    response_model=list[CountryVisaReferencePublicSchema],
    description="Get all visa types related to a specific country",
    name="reference:country-visa-type-list"
)
async def country_visa_type_list(
        country_id: int,
        country_visa_repo: CountryVisasRepository = Depends(get_repository(CountryVisasRepository))
):
    result = await country_visa_repo.get_list(country_id=country_id)
    return result


urgency_list = router.get(
    path="/urgencies",
    response_model=list[UrgencyPublicSchema],
    status_code=200,
    summary="Get all urgencies - unpaginated",
    name="reference:urgency-list"
)(urgency_list)
