from fastapi import APIRouter, Depends

from app.api.dependencies.db import get_repository
from app.api.helpers import paginate
from app.database.repositories.visa_types import VisaTypesRepository
from app.exceptions import NotFoundException
from app.schemas.pagination import PageParamsSchema, PagedResponseSchema
from app.schemas.visa_type import VisaTypePublicSchema, VisaTypeFilterSchema, VisaTypeUpdateSchema


router = APIRouter()


@router.get(
    path="/",
    response_model=PagedResponseSchema,
    name="admin:visa_type-list"
)
async def visa_type_list(
        filters: VisaTypeFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        visa_types_repo: VisaTypesRepository = Depends(get_repository(VisaTypesRepository))
):
    results = await visa_types_repo.get_list()
    return paginate(
        page_params,
        results,
        VisaTypePublicSchema
    )


@router.get(
    path="/{visa_type_id}",
    response_model=VisaTypePublicSchema,
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


@router.put(
    path="/{visa_type_id}",
    response_model=VisaTypePublicSchema,
    name="admin:visa_type-update"
)
async def visa_type_update(
        visa_type_id: int,
        data: VisaTypeUpdateSchema,
        visa_types_repo: VisaTypesRepository = Depends(get_repository(VisaTypesRepository))
):
    visa_type = await visa_types_repo.update(
        visa_type_id=visa_type_id,
        data=data
    )

    if not visa_type:
        raise NotFoundException()
    return visa_type
