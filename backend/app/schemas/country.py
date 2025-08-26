from typing import Optional, Annotated

from fastapi import Query

from app.schemas.core import CoreSchema, IDSchemaMixin


class CountryBaseSchema(CoreSchema):
    name: Optional[str] = None
    alpha2: Optional[str] = None
    alpha3: Optional[str] = None


class CountryPublicSchema(IDSchemaMixin, CountryBaseSchema):
    pass


class CountryFilterSchema(CoreSchema):
    name: Annotated[str | None, Query(max_length=50, description="Filter by country's name")] = None
