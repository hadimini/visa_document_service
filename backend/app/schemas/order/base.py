from enum import Enum
from typing import Optional

from pydantic import Field

from app.models import Order
from app.schemas.applicant import (
    ApplicantPublicSchema,
    ApplicantCreateSchema,
    ApplicantUpdateSchema
)
from app.schemas.core import (
    CoreSchema,
    IDSchemaMixin,
    ArchivedAtSchemaMixin,
    DateTimeSchemaMixin,
    CompletedAtSchemaMixin
)
from app.schemas.country import CountryReferencePublicSchema
from app.schemas.urgency import UrgencyResponseSchema
from app.schemas.user import UserResponseSchema
from app.schemas.visa_duration import VisaDurationPublicSchema
from app.schemas.visa_type import VisaTypeResponseSchema


class OrderStatusEnum(str, Enum):
    DRAFT = Order.STATUS_DRAFT
    NEW = Order.STATUS_NEW
    IN_PROGRESS = Order.STATUS_IN_PROGRESS
    COMPLETED = Order.STATUS_COMPLETED
    CANCELED = Order.STATUS_CANCELED


class BaseOrderSchema(CoreSchema):
    status: Optional[OrderStatusEnum] = None
    country_id: Optional[int] = None
    created_by_id: Optional[int] = None
    urgency_id: Optional[int] = None
    visa_duration_id: Optional[int] = None
    visa_type_id: Optional[int] = None


class BaseOrderListSchema(
    ArchivedAtSchemaMixin,
    DateTimeSchemaMixin,
    CompletedAtSchemaMixin,
    IDSchemaMixin,
    # BaseOrderSchema
):
    MODEL_TYPE: str = Field(default_factory=lambda: Order.get_model_type())
    status: OrderStatusEnum
    number: str
    country: CountryReferencePublicSchema
    created_by: UserResponseSchema
    urgency: UrgencyResponseSchema
    visa_duration: VisaDurationPublicSchema
    visa_type: VisaTypeResponseSchema


class BaseOrderPublicSchema(BaseOrderListSchema):
    applicant: Optional[ApplicantPublicSchema] = None


class BaseOrderCreateSchema(CoreSchema):
    status: Optional[OrderStatusEnum] = None
    country_id: int
    created_by_id: Optional[int] = None
    urgency_id: int
    visa_duration_id: int
    visa_type_id: int


class BaseOrderUpdateSchema(BaseOrderSchema):
    applicant: Optional[ApplicantUpdateSchema] = None


class BaseOrdersFilterSchema(BaseOrderSchema):
    status: Optional[OrderStatusEnum] = None
    country_id: Optional[int] = None
    urgency_id: Optional[int] = None
    visa_duration_id: Optional[int] = None
    visa_type_id: Optional[int] = None
