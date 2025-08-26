from typing import Optional

from app.schemas.core import CoreSchema, IDSchemaMixin


class CountryBaseSchema(CoreSchema):
    name: Optional[str] = None
    alpha2: Optional[str] = None
    alpha3: Optional[str] = None


class CountryPublicSchema(IDSchemaMixin, CountryBaseSchema):
    pass
