from typing import Optional

from app.schemas.applicant import ApplicantPublicSchema
from app.schemas.client import ClientPublicSchema
from app.schemas.core import (
    CoreSchema
)
from app.schemas.order.base import (
    BaseOrderPublicSchema,
    BaseOrderCreateSchema,
    BaseOrderUpdateSchema
)
from app.schemas.pagination import PagedResponseSchema


class AdminOrderListSchema(BaseOrderPublicSchema):
    client: ClientPublicSchema


class AdminOrderDetailSchema(AdminOrderListSchema):
    applicant: ApplicantPublicSchema


class AdminOrderCreateSchema(BaseOrderCreateSchema):
    client_id: int


class AdminOrderUpdateSchema(BaseOrderUpdateSchema):
    client_id: Optional[int] = None


class AdminOrderListSchema(PagedResponseSchema, CoreSchema):
    items: list[AdminOrderDetailSchema]
