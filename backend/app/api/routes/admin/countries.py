from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.api.routes.base.countries import country_list, country_detail
from app.database.repositories.audit import AuditRepository
from app.database.repositories.countries import CountriesRepository
from app.exceptions import NotFoundException
from app.models.audit import LogEntry
from app.models.countries import Country
from app.models.users import User
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.pagination import PagedResponseSchema
from app.schemas.country import CountryPublicSchema, CountryUpdateSchema

router = APIRouter()


country_list = router.get(
    path="/",
    response_model=PagedResponseSchema,
    name="admin:country-list"
)(country_list)

country_detail = router.get(
    path="/{country_id}",
    response_model=CountryPublicSchema,
    name="admin:country-detail"
)(country_detail)


@router.put(
    path="/{country_id}",
    response_model=CountryPublicSchema,
    name="admin:country-update"
)
async def update_country(
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
