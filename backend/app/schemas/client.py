from enum import Enum
from typing import Annotated, Optional

from fastapi import Query
from pydantic import Field, StringConstraints, EmailStr

from app.models import Client
from app.schemas.core import CoreSchema, IDSchemaMixin
from app.schemas.tariff import TariffPublicSchema
from app.schemas.pagination import PagedResponseSchema


class ClientTypeEnum(str, Enum):
    INDIVIDUAL = Client.TYPE_INDIVIDUAL
    LEGAL = Client.TYPE_LEGAL


class ClientBaseSchema(CoreSchema):
    tariff: Optional[TariffPublicSchema] = None
    name: Optional[str] = None
    type: Optional[ClientTypeEnum] = None


class ClientCreateSchema(CoreSchema):
    tariff_id: int
    email: EmailStr
    name: Annotated[str, StringConstraints(min_length=3, max_length=100, pattern="^[a-zA-Z0-9 ]+$")]
    type: ClientTypeEnum


class ClientPublicSchema(IDSchemaMixin, ClientBaseSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: Client.get_model_type())


class ClientFilterSchema(CoreSchema):
    name: Annotated[str | None, Query(max_length=50, description="Filter by client's name")] = None
    type: Optional[ClientTypeEnum] = None


class ClientListResponseSchema(PagedResponseSchema, CoreSchema):
    items: list[ClientPublicSchema]
