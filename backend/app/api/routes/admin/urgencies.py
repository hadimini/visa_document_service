from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.api.routes.base.urgencies import urgency_list
from app.database.repositories.audit import AuditRepository
from app.database.repositories.urgencies import UrgenciesRepository
from app.exceptions import NotFoundException
from app.models.audit import LogEntry
from app.models.urgencies import Urgency
from app.models.users import User
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.urgency import UrgencyPublicSchema, UrgencyCreateSchema, UrgencyUpdateSchema

router = APIRouter()


urgency_list = router.get(
    path="/",
    response_model=list[UrgencyPublicSchema],
    name="admin:urgency-list"
)(urgency_list)


@router.get(
    path="/{urgency_id}",
    response_model=UrgencyPublicSchema,
    name="admin:urgency-detail"
)
async def urgency_detail(
        urgency_id: int,
        urgencies_repo: UrgenciesRepository = Depends(get_repository(UrgenciesRepository))
):
    urgency = await urgencies_repo.get_by_id(urgency_id=urgency_id)

    if not urgency:
        raise NotFoundException()

    return urgency


@router.post(
    path="/",
    response_model=UrgencyPublicSchema,
    status_code=status.HTTP_201_CREATED,
    name="admin:urgency-create",
)
async def urgency_create(
        data: UrgencyCreateSchema,
        current_user: User = Depends(get_current_active_user),
        urgencies_repo: UrgenciesRepository = Depends(get_repository(UrgenciesRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
):
    urgency = await urgencies_repo.create(data=data)
    await audit_repo.create(
        data=LogEntryCreateSchema(
            user_id=current_user.id,
            action=LogEntry.ACTION_CREATE,
            model_type=Urgency.get_model_type(),
            target_id=urgency.id,
        )
    )
    return urgency


@router.put(
    path="/{urgency_id}",
    response_model=UrgencyPublicSchema,
    name="admin:urgency-update"
)
async def urgency_update(
        urgency_id: int,
        data: UrgencyUpdateSchema,
        current_user: User = Depends(get_current_active_user),
        urgencies_repo: UrgenciesRepository = Depends(get_repository(UrgenciesRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository))
):
    urgency = await urgencies_repo.update(
        urgency_id=urgency_id,
        data=data
    )

    if not urgency:
        raise NotFoundException()

    await audit_repo.create(
        data=LogEntryCreateSchema(
            user_id=current_user.id,
            action=LogEntry.ACTION_UPDATE,
            model_type=Urgency.get_model_type(),
            target_id=urgency.id,
        )
    )
    return urgency
