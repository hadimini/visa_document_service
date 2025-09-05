from typing import Annotated

from fastapi import Query
from pydantic import Field

from app.models import VisaType
from app.schemas.core import CoreSchema, IDSchemaMixin
from app.schemas.pagination import PagedResponseSchema


class VisaTypeBaseSchema(CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: VisaType.get_model_type())
    name: str | None = None


class VisaTypeCreateSchema(CoreSchema):
    name: str


class VisaTypeUpdateSchema(CoreSchema):
    name: str


class VisaTypeResponseSchema(IDSchemaMixin, VisaTypeBaseSchema):
    pass


class VisaTypeFilterSchema(CoreSchema):
    name: Annotated[str | None, Query(max_length=50, description="Filter by visa type's name")] = None


class VisaTypeListResponseSchema(PagedResponseSchema, CoreSchema):
    items: list[VisaTypeResponseSchema]
