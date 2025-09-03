from app.schemas.core import CoreSchema, IDSchemaMixin


class VisaDurationsBaseSchema(CoreSchema):
    name: str | None
    term: str | None
    entry: str | None


class VisaDurationPublicSchema(IDSchemaMixin, VisaDurationsBaseSchema):
    pass
