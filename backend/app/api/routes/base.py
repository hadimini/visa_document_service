from fastapi import Depends

from app.api.dependencies.db import get_repository
from app.api.helpers import paginate

from app.database.repositories.countries import CountriesRepository
from app.exceptions import NotFoundException
from app.models.countries import Country
from app.schemas.pagination import PageParamsSchema
from app.schemas.country import CountryPublicSchema, CountryFilterSchema


async def country_list(
        filters: CountryFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        countries_repo: CountriesRepository = Depends(get_repository(CountriesRepository)),

):
    results: list[Country] = await countries_repo.get_list(filters=filters, page_params=page_params)
    return paginate(
        page_params,
        results,
        CountryPublicSchema
    )


async def country_detail(
        country_id: int,
        countries_repo: CountriesRepository = Depends(get_repository(CountriesRepository)),
):
    country = await countries_repo.get_by_id(country_id=country_id)

    if not country:
        raise NotFoundException()
    return country
