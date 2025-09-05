from typing import Optional, Any

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository

from app.database.repositories.audit import AuditRepository
from app.database.repositories.countries import CountriesRepository
from app.database.repositories.country_visas import CountryVisasRepository
from app.exceptions import NotFoundException
from app.models import Country, CountryVisa, LogEntry, User
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.country import (
    CountryListResponseSchema,
    CountryAdminPublicSchema,
    CountryUpdateSchema,
    CountryFilterSchema
)
from app.schemas.country_visa import CountryVisaAdminPublicSchema, CountryVisaAdminUpdateSchema
from app.schemas.pagination import PageParamsSchema

router = APIRouter()


@router.get(
    path="",
    response_model=CountryListResponseSchema,
    summary="Country list page",
    name="admin:country-list"
)
async def country_list(
        query_filters: CountryFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        countries_repo: CountriesRepository = Depends(get_repository(CountriesRepository)),
):
    result: dict[str, Any] = await countries_repo.get_paginated_list(query_filters=query_filters, page_params=page_params)
    return result


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
    country = await countries_repo.get_by_id(country_id=country_id, populate_visa_data=True)

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
    await audit_repo.create(data=entry_log)
    return country


@router.get(
    path="/{country_id}/country_visa/{country_visa_id}",
    response_model=CountryVisaAdminPublicSchema,
    name="admin:country_visa-detail"
)
async def country_visa_detail(
        country_id: int,
        country_visa_id: int,
        country_visas_repo: CountryVisasRepository = Depends(get_repository(CountryVisasRepository)),
):
    country_visa: Optional[CountryVisa] = await country_visas_repo.get_by_id(
        country_visa_id=country_visa_id, populate_duration_data=True
    )

    if not country_visa:
        raise NotFoundException()

    return country_visa


@router.put(
    path="/{country_id}/country_visa/{country_visa_id}",
    response_model=CountryVisaAdminPublicSchema,
    name="admin:country_visa-update"
)
async def country_visa_update(
        country_id: int,
        data: CountryVisaAdminUpdateSchema,
        country_visa_id: int,
        country_visas_repo: CountryVisasRepository = Depends(get_repository(CountryVisasRepository)),
):
    country_visa: Optional[CountryVisa] = await country_visas_repo.update(country_visa_id=country_visa_id, data=data)

    if not country_visa:
        raise NotFoundException()

    country_visa = await country_visas_repo.get_by_id(country_visa_id=country_visa_id, populate_duration_data=True)

    return country_visa
