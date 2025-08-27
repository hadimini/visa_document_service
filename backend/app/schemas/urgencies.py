from app.schemas.core import CoreSchema, IDSchemaMixin


class UrgencyBaseSchema(CoreSchema):
    name: str | None = None


class UrgencyCreateSchema(CoreSchema):
    name: str


class UrgencyUpdateSchema(CoreSchema):
    name: str


class UrgencyPublicSchema(IDSchemaMixin, UrgencyBaseSchema):
    pass
