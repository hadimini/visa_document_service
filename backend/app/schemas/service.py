from decimal import Decimal
from enum import Enum
from typing import Annotated, Optional

from fastapi import Query
from pydantic import Field, ConfigDict

from app.models import Service, TariffService
from app.schemas.core import (
    ArchivedAtSchemaMixin,
    DateTimeSchemaMixin,
    CoreSchema,
    IDSchemaMixin
)
from app.schemas.pagination import PagedResponseSchema
from app.schemas.tariff import TariffPublicSchema


class FeeTypeEnum(str, Enum):
    CONSULAR = Service.FEE_TYPE_CONSULAR
    GENERAL = Service.FEE_TYPE_GENERAL


class ServiceBaseSchema(CoreSchema):
    """
    Base schema for Service model with common fields.
    """
    name: Optional[str] = Field(min_length=1, max_length=255, description="Service name")
    # fee_type: Optional[str] = Field(..., description="Fee type (consular or general)")
    fee_type: Optional[FeeTypeEnum] = None

    # Optional foreign keys
    country_id: Optional[int] = Field(default=None, description="Id of the associated country")
    urgency_id: Optional[int] = Field(default=None, description="Id of the associated urgency")
    visa_duration_id: Optional[int] = Field(default=None, description="Id of the associated visa duration")
    visa_type_id: Optional[int] = Field(default=None, description="Id of the associated visa type")


class TariffServiceCreateSchema(CoreSchema):
    """
    Schema for Tariff Service model.
    """
    price: Decimal = Field(gt=0, description="Price must be positive")
    tax: Decimal = Field(ge=0, description="Tax cannot be negative")
    tariff_id: int = Field(gt=0, description="Id of the tariff")


class ServiceCreateSchema(ServiceBaseSchema):
    """
    Schema for creating a new Service.
    """
    name: str = Field(min_length=1, max_length=255, description="Service name")
    fee_type: FeeTypeEnum
    tariff_services: Optional[list[TariffServiceCreateSchema]] = None

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "name": "Business Visa",
                "fee_type": "consular",
                "country_id": 1,
                "urgency_id": 2,
                "visa_duration_id": 3,
                "visa_type_id": 4,
                "tariff_services": [
                    {
                        "price": 10.3,
                        "tax": 0.15,
                        "tariff_id": 1
                    }
                ]
            }
        }
    )


class TariffServiceDetailSchema(IDSchemaMixin, CoreSchema):
    """
    Schema for Tariff Service model.
    """
    MODEL_TYPE: str = Field(default_factory=lambda: TariffService.get_model_type())
    price: Decimal
    tax: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total: Decimal
    tariff: TariffPublicSchema


class ServiceResponseSchema(
    ArchivedAtSchemaMixin,
    DateTimeSchemaMixin,
    IDSchemaMixin,
    ServiceBaseSchema
):
    """
    Schema for Service with all fields
    """
    MODEL_TYPE: str = Field(default_factory=lambda: Service.get_model_type())
    tariff_services: Optional[list[TariffServiceDetailSchema]] = None


class ServiceUpdateSchema(CoreSchema):
    """
    Schema for updating an existing Service.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    fee_type: Optional[FeeTypeEnum] = None
    country_id: Optional[int] = None
    urgency_id: Optional[int] = None
    visa_duration_id: Optional[int] = None
    visa_type_id: Optional[int] = None


class ServiceFilterSchema(CoreSchema):
    """
    Schema for filtering Service in admin panel.
    """
    name: Annotated[str | None, Query(max_length=250, description="Filter by service's name")] = None
    fee_type: Optional[FeeTypeEnum] = None
    country_id: Optional[int] = None
    urgency_id: Optional[int] = None
    visa_duration_id: Optional[int] = None
    visa_type_id: Optional[int] = None


class ServiceListResponseSchema(PagedResponseSchema, CoreSchema):
    items: list[ServiceResponseSchema]
