from app.schemas.core import CoreSchema, IDSchemaMixin


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
