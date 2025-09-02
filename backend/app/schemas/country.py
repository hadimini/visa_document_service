from typing import Optional, Annotated

from fastapi import Query

from app.schemas.core import CoreSchema, IDSchemaMixin
from app.schemas.visa_type import VisaTypePublicSchema


class CountryBaseSchema(CoreSchema):
    name: Optional[str] = None
    alpha2: Optional[str] = None
    alpha3: Optional[str] = None
    available_for_order: Optional[bool] = False


class CountryVisaSchema(CoreSchema):
    id: int
    is_active: bool
    visa_type: VisaTypePublicSchema


class CountryVisaDataSchema(CoreSchema):
    attached: Optional[list[CountryVisaSchema]] = None
    available: Optional[list[VisaTypePublicSchema]] = None


class CountryAdminPublicSchema(IDSchemaMixin, CountryBaseSchema):
    visa_data: CountryVisaDataSchema = None


class CountryReferencePublicSchema(IDSchemaMixin, CountryBaseSchema):
    pass


class CountryUpdateSchema(CoreSchema):
    available_for_order: bool
    visa_type_ids: Optional[list[int]] = None


class CountryFilterSchema(CoreSchema):
    name: Annotated[str | None, Query(max_length=50, description="Filter by country's name")] = None
    available_for_order: Optional[bool] = False
