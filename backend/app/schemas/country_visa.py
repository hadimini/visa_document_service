from typing import Optional

from pydantic import Field

from app.schemas.core import CoreSchema, IDSchemaMixin
from app.schemas.visa_type import VisaTypePublicSchema


class CountryVisaBaseSchema(CoreSchema):
    country_id: int | None = None
    visa_type_id: int | None = None
    is_active: bool


class CountryVisaCreateSchema(CoreSchema):
    country_id: int
    visa_type_id: int
    is_active: bool


class CountryVisaUpdateSchema(CoreSchema):
    country_id: int
    visa_type_id: int
    is_active: bool


class CountryVisaPublicSchema(IDSchemaMixin, CountryVisaBaseSchema):
    pass


class CountryVisaDurationAdminPublicSchema(IDSchemaMixin, CoreSchema):
    name: str


class CountryVisaAdminPublicSchema(IDSchemaMixin, CoreSchema):
    is_active: bool
    visa_type: VisaTypePublicSchema
    visa_durations: Optional[list[CountryVisaDurationAdminPublicSchema]] = Field(default_factory=list)


class CountryVisaAdminUpdateSchema(CoreSchema):
    is_active: Optional[bool] = None
    visa_duration_ids: Optional[list[int]] = Field(default_factory=list)


class CountryVisaReferencePublicSchema(IDSchemaMixin):
    visa_type: VisaTypePublicSchema
    is_active: bool
