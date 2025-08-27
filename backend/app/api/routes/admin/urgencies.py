from fastapi import APIRouter, Depends, status

from app.api.dependencies.db import get_repository
from app.api.helpers import paginate
from app.database.repositories.audit import AuditRepository
from app.database.repositories.urgencies import UrgenciesRepository
from app.exceptions import NotFoundException
from app.schemas.urgencies import UrgencyPublicSchema, UrgencyCreateSchema, UrgencyUpdateSchema

router = APIRouter()


@router.get(
    path="/",
    response_model=list[UrgencyPublicSchema],
    name="admin:urgency-list"
)
async def urgency_list(
        urgencies_repo: UrgenciesRepository = Depends(get_repository(UrgenciesRepository))
):
    results = await urgencies_repo.get_list()
    print("results", results)
    return results


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
        name="admin:urgency-create",
    status_code=status.HTTP_201_CREATED
)
async def urgency_create(
        data: UrgencyCreateSchema,
        urgencies_repo: UrgenciesRepository = Depends(get_repository(UrgenciesRepository))
):
    urgency = await urgencies_repo.create(data=data)
    return urgency


@router.put(
    path="/{urgency_id}",
    response_model=UrgencyPublicSchema,
    name="admin:urgency-update"
)
async def urgency_update(
        urgency_id: int,
        data: UrgencyUpdateSchema,
        urgencies_repo: UrgenciesRepository = Depends(get_repository(UrgenciesRepository))
):
    urgency = await urgencies_repo.update(
        urgency_id=urgency_id,
        data=data
    )

    if not urgency:
        raise NotFoundException()

    return urgency
