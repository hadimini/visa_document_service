from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.database.repositories.audit import AuditRepository
from app.database.repositories.visa_types import VisaTypesRepository
from app.exceptions import NotFoundException
from app.models.audit import LogEntry
from app.models.users import User
from app.models.visa_types import VisaType
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.pagination import PageParamsSchema
from app.schemas.visa_type import (
    VisaTypeResponseSchema,
    VisaTypeFilterSchema,
    VisaTypeUpdateSchema,
    VisaTypeCreateSchema,
    VisaTypeListResponseSchema
)

router = APIRouter()


@router.get(
    path="",
    response_model=VisaTypeListResponseSchema,
    name="admin:visa_type-list"
)
async def visa_type_list(
        query_filters: VisaTypeFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        visa_types_repo: VisaTypesRepository = Depends(get_repository(VisaTypesRepository))
):
    result = await visa_types_repo.get_list(query_filters=query_filters, page_params=page_params)  # todo: apply filters and pagination
    return result


@router.get(
    path="/{visa_type_id}",
    response_model=VisaTypeResponseSchema,
    name="admin:visa_type-detail"
)
async def visa_type_detail(
        visa_type_id: int,
        visa_types_repo: VisaTypesRepository = Depends(get_repository(VisaTypesRepository))
):
    visa_type = await visa_types_repo.get_by_id(visa_type_id=visa_type_id)
    if not visa_type:
        raise NotFoundException()
    return visa_type


@router.post(
    path="",
    response_model=VisaTypeResponseSchema,
    name="admin:visa_type-create",
    status_code=status.HTTP_201_CREATED
)
async def visa_type_create(
        data: VisaTypeCreateSchema,
        current_user: User = Depends(get_current_active_user),
        visa_types_repo: VisaTypesRepository = Depends(get_repository(VisaTypesRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
):
    visa_type = await visa_types_repo.create(data=data)

    await audit_repo.create(
        data=LogEntryCreateSchema(
            user_id=current_user.id,
            action=LogEntry.ACTION_CREATE,
            model_type=VisaType.get_model_type(),
            target_id=visa_type.id,
        )
    )
    return visa_type


@router.put(
    path="/{visa_type_id}",
    response_model=VisaTypeResponseSchema,
    name="admin:visa_type-update"
)
async def visa_type_update(
        visa_type_id: int,
        data: VisaTypeUpdateSchema,
        current_user: User = Depends(get_current_active_user),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
        visa_types_repo: VisaTypesRepository = Depends(get_repository(VisaTypesRepository))
):
    visa_type = await visa_types_repo.update(
        visa_type_id=visa_type_id,
        data=data
    )

    if not visa_type:
        raise NotFoundException()

    await audit_repo.create(
        data=LogEntryCreateSchema(
            user_id=current_user.id,
            action=LogEntry.ACTION_UPDATE,
            model_type=VisaType.get_model_type(),
            target_id=visa_type.id,
        )
    )

    return visa_type
