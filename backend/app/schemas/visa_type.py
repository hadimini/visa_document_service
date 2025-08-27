from typing import Annotated

from fastapi import Query

from app.schemas.core import CoreSchema, IDSchemaMixin


class VisaTypeBaseSchema(CoreSchema):
    name: str | None = None


class VisaTypeCreateSchema(CoreSchema):
    name: str


class VisaTypePublicSchema(IDSchemaMixin, VisaTypeBaseSchema):
    pass


class VisaTypeFilterSchema(CoreSchema):
    name: Annotated[str | None, Query(max_length=50, description="Filter by visa type's name")] = None
