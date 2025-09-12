from typing import Optional

from app.schemas.applicant import ApplicantPublicSchema
from app.schemas.client import ClientPublicSchema
from app.schemas.core import (
    CoreSchema
)
from app.schemas.order.base import (
    BaseOrderListSchema,
    BaseOrderCreateSchema,
    BaseOrderUpdateSchema,
    BaseOrdersFilterSchema
)
from app.schemas.pagination import PagedResponseSchema


class AdminOrderListSchema(BaseOrderListSchema):
    client: ClientPublicSchema


class AdminOrderDetailSchema(AdminOrderListSchema):
    applicant: Optional[ApplicantPublicSchema] = None


class AdminOrderCreateSchema(BaseOrderCreateSchema):
    client_id: int


class AdminOrderUpdateSchema(BaseOrderUpdateSchema):
    client_id: Optional[int] = None


class AdminOrderPaginatedListSchema(PagedResponseSchema, CoreSchema):
    items: list[AdminOrderListSchema]


class AdminOrderFilterSchema(BaseOrdersFilterSchema):
    created_by_id: Optional[int] = None
    client_id: Optional[int] = None
