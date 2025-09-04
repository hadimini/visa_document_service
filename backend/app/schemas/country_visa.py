from typing import Optional

from pydantic import Field

from app.models import CountryVisa
from app.schemas.core import CoreSchema, IDSchemaMixin
from app.schemas.visa_duration import VisaDurationPublicSchema
from app.schemas.visa_type import VisaTypePublicSchema


class CountryVisaBaseSchema(CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: CountryVisa.get_model_type())
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


class CountryVisaDurationDataSchema(CoreSchema):
    attached: Optional[list[VisaDurationPublicSchema]] = None
    available: Optional[list[VisaDurationPublicSchema]] = None


class CountryVisaAdminPublicSchema(IDSchemaMixin, CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: CountryVisa.get_model_type())
    is_active: bool
    visa_type: VisaTypePublicSchema
    duration_data: Optional[CountryVisaDurationDataSchema] = None


class CountryVisaAdminUpdateSchema(CoreSchema):
    is_active: Optional[bool] = None
    visa_duration_ids: Optional[list[int]] = None


class CountryVisaReferencePublicSchema(IDSchemaMixin):
    visa_type: VisaTypePublicSchema
    is_active: bool
    visa_durations: Optional[list[VisaDurationPublicSchema]] = None
