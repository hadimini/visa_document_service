from typing import Annotated, Literal, Optional

from fastapi import Query
from pydantic import StringConstraints

from app.schemas.core import CoreSchema, IDSchemaMixin


class ClientBaseSchema(CoreSchema):
    tariff_id: Optional[int] = None
    name: Optional[str] = None
    type: Literal["individual", "legal"] | None = None


class ClientCreateSchema(CoreSchema):
    tariff_id: int
    name: Annotated[str, StringConstraints(min_length=3, max_length=100, pattern="^[a-zA-Z0-9 ]+$")]
    type: Literal["individual", "legal"]


class ClientInDBSchema(IDSchemaMixin):
    pass


class ClientPublicSchema(IDSchemaMixin, ClientBaseSchema):
    pass


class ClientFilterSchema(CoreSchema):
    name: Annotated[str | None, Query(max_length=50, description="Filter by client's name")] = None
    type: Literal["individual", "legal"] | None = None
