from typing import Annotated

from pydantic import StringConstraints

from app.schemas.core import CoreSchema, IDSchemaMixin


class TariffBaseSchema(CoreSchema):
    name: Annotated[str, StringConstraints(min_length=3, max_length=100)] | None = None
    is_default: bool = False


class TariffCreateSchema(TariffBaseSchema):
    name: Annotated[str, StringConstraints(min_length=3, max_length=100)]
    is_default: bool


class TariffPublicSchema(IDSchemaMixin, TariffBaseSchema):
    pass
