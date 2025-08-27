from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.database.repositories.audit import AuditRepository
from app.database.repositories.country_visas import CountryVisasRepository
from app.exceptions import NotFoundException
from app.models import CountryVisa
from app.models.audit import LogEntry
from app.models.users import User
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.country_visa import CountryVisaCreateSchema, CountryVisaPublicSchema

router = APIRouter()

@router.get(
    "/",
    response_model=list[CountryVisaPublicSchema],
    status_code=200,
    name="admin:country_visa-list",
)
async def country_visa_list(
        country_visas_repo: CountryVisasRepository = Depends(get_repository(CountryVisasRepository)),
):
    results = await country_visas_repo.get_list()
    return results


@router.post(
    path="/",
    response_model=CountryVisaPublicSchema,
    status_code=201,
    name="admin:country_visa-create"
)
async def country_visa_create(
        data: CountryVisaCreateSchema,
        current_user: User = Depends(get_current_active_user),
        country_visas_repo: CountryVisasRepository = Depends(get_repository(CountryVisasRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
):
    country_visa = await country_visas_repo.create(data=data)

    await audit_repo.create(
        new_entry=LogEntryCreateSchema(
            user_id=current_user.id,
            action=LogEntry.ACTION_CREATE,
            model_type=CountryVisa.get_model_type(),
            target_id=country_visa.id,
        )
    )
    return country_visa


@router.get(
    path="/{country_visa_id}",
    response_model=CountryVisaPublicSchema,
    status_code=200,
    name="admin:country_visa-detail",
)
async def country_visa_detail(
        country_visa_id: int,
        country_visas_repo: CountryVisasRepository = Depends(get_repository(CountryVisasRepository)),
):
    country_visa = await country_visas_repo.get_by_id(country_visa_id=country_visa_id)

    if country_visa is None:
        raise NotFoundException()

    return country_visa
