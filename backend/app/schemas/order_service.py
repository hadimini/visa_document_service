from decimal import Decimal
from typing import Optional

from pydantic import Field

from app.models import OrderService, Service, TariffService
from app.schemas.core import CoreSchema, IDSchemaMixin


class OrderServiceBaseSchema(CoreSchema):
    price: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total: Optional[Decimal] = None


class ServicePublicSchema(IDSchemaMixin, CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: Service.get_model_type())
    name: Optional[str] = None
    fee_type: Optional[str] = None  # todo: try lambda get {value: ... , label: ...}


class OrderServicePublicSchema(IDSchemaMixin, OrderServiceBaseSchema, CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: OrderService.get_model_type())
    service: Optional[ServicePublicSchema] = None


class TariffServicePublicSchema(IDSchemaMixin, CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: TariffService.get_model_type())
    service: Optional[ServicePublicSchema] = None
    price: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total: Optional[Decimal] = None


class OrderServicesDataSchema(CoreSchema):
    attached: Optional[list[OrderServicePublicSchema]] = None
    available: Optional[list[TariffServicePublicSchema]] = None


class OrderServicesUpdateSchema(CoreSchema):
    tariff_services_ids: Optional[list[int]] = None
