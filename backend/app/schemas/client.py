from typing import Annotated, Literal, Optional

from fastapi import Query
from pydantic import Field, StringConstraints

from app.models import Client
from app.schemas.core import CoreSchema, IDSchemaMixin
from app.schemas.tariff import TariffPublicSchema
from app.schemas.pagination import PagedResponseSchema


class ClientBaseSchema(CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: Client.get_model_type())
    tariff: Optional[TariffPublicSchema] = None
    name: Optional[str] = None
    type: Literal["individual", "legal"] | None = None


class ClientCreateSchema(CoreSchema):
    tariff_id: int
    name: Annotated[str, StringConstraints(min_length=3, max_length=100, pattern="^[a-zA-Z0-9 ]+$")]
    type: Literal["individual", "legal"]


class ClientResponseSchema(IDSchemaMixin, ClientBaseSchema):
    pass


class ClientFilterSchema(CoreSchema):
    name: Annotated[str | None, Query(max_length=50, description="Filter by client's name")] = None
    type: Literal["individual", "legal"] | None = None


class ClientListResponseSchema(PagedResponseSchema, CoreSchema):
    items: list[ClientResponseSchema]
