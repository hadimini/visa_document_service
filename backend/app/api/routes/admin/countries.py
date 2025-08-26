from fastapi import APIRouter, Depends

from app.api.dependencies.auth import role_required
from app.api.dependencies.db import get_repository
from app.api.helpers import paginate

from app.database.repositories.countries import CountriesRepository
from app.models.countries import Country
from app.models.users import User
from app.schemas.pagination import PageParamsSchema, PagedResponseSchema
from app.schemas.country import CountryPublicSchema, CountryFilterSchema

router = APIRouter()


@router.get("/", response_model=PagedResponseSchema, name="admin:country-list")
async def country_list(
        filters: CountryFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        current_user: User = Depends(role_required(User.ROLE_ADMIN)),
        countries_repo: CountriesRepository = Depends(get_repository(CountriesRepository)),

):
    results: list[Country] = await countries_repo.get_all(filters=filters, page_params=page_params)
    return paginate(
        page_params,
        results,
        CountryPublicSchema
    )
