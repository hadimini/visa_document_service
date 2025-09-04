from pydantic import Field

from app.models.urgencies import Urgency
from app.schemas.core import CoreSchema, IDSchemaMixin


class UrgencyBaseSchema(CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: Urgency.get_model_type())
    name: str | None = None


class UrgencyCreateSchema(CoreSchema):
    name: str


class UrgencyUpdateSchema(CoreSchema):
    name: str


class UrgencyPublicSchema(IDSchemaMixin, UrgencyBaseSchema):
    pass
