from pydantic import Field

from app.models import VisaDuration
from app.schemas.core import CoreSchema, IDSchemaMixin


class VisaDurationsBaseSchema(CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: VisaDuration.get_model_type())
    name: str | None
    term: str | None
    entry: str | None


class VisaDurationPublicSchema(IDSchemaMixin, VisaDurationsBaseSchema):
    pass
