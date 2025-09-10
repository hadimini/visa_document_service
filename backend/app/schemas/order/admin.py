from typing import Optional

from app.schemas.applicant import (
    ApplicantPublicSchema,
    ApplicantCreateSchema,
    ApplicantUpdateSchema
)
from app.schemas.client import ClientPublicSchema
from app.schemas.core import (
    CoreSchema
)
from app.schemas.order.base import BaseOrderSchema, BaseOrderPublicSchema
from app.schemas.pagination import PagedResponseSchema


class BaseAdminOrderSchema(BaseOrderSchema):
    client_id: Optional[int] = None


class AdminOrderListSchema(BaseOrderPublicSchema):
    client: ClientPublicSchema


class AdminOrderDetailSchema(AdminOrderListSchema):
    applicant: ApplicantPublicSchema


class AdminOrderCreateSchema(BaseAdminOrderSchema):
    applicant: ApplicantCreateSchema


class AdminOrderUpdateSchema(BaseAdminOrderSchema):
    applicant: ApplicantUpdateSchema


class AdminOrderListSchema(PagedResponseSchema, CoreSchema):
    items: list[AdminOrderDetailSchema]
