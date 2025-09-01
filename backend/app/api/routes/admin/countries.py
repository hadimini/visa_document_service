from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.api.helpers import paginate
from app.database.repositories.audit import AuditRepository
from app.database.repositories.countries import CountriesRepository
from app.exceptions import NotFoundException
from app.models.audit import LogEntry
from app.models.countries import Country
from app.models.users import User
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.pagination import PagedResponseSchema, PageParamsSchema
from app.schemas.country import CountryAdminPublicSchema, CountryUpdateSchema, CountryFilterSchema

router = APIRouter()


@router.get(
    path="",
    response_model=PagedResponseSchema,
    summary="Country list page",
    name="admin:country-list"
)
async def country_list(
        filters: CountryFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        countries_repo: CountriesRepository = Depends(get_repository(CountriesRepository)),

):
    results: list[Country] = await countries_repo.get_paginated_list(filters=filters, page_params=page_params)
    return paginate(
        page_params,
        results,
        CountryAdminPublicSchema
    )


@router.get(
    path="/{country_id}",
    response_model=CountryAdminPublicSchema,
    summary="Country detail page",
    name="admin:country-detail"
)
async def country_detail(
        country_id: int,
        countries_repo: CountriesRepository = Depends(get_repository(CountriesRepository)),
):
    country = await countries_repo.get_by_id(country_id=country_id)

    if not country:
        raise NotFoundException()
    return country


@router.put(
    path="/{country_id}",
    response_model=CountryAdminPublicSchema,
    summary="Country update page",
    name="admin:country-update"
)
async def country_update(
        country_id: int,
        data: CountryUpdateSchema,
        current_user: User = Depends(get_current_active_user),
        countries_repo: CountriesRepository = Depends(get_repository(CountriesRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
):
    country = await countries_repo.update(country_id=country_id, data=data)

    if country is None:
        raise NotFoundException()

    entry_log = LogEntryCreateSchema(
        user_id=current_user.id,
        action=LogEntry.ACTION_UPDATE,
        model_type=Country.get_model_type(),
        target_id=country_id
    )
    await audit_repo.create(new_entry=entry_log)
    return country
