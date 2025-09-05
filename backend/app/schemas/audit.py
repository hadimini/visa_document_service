from typing import Optional

from pydantic import Field

from app.models import LogEntry
from app.schemas.core import CoreSchema, CreatedAtSchemaMixin, IDSchemaMixin


class LogEntryBaseSchema(CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: LogEntry.get_model_type())
    user_id: Optional[int] = None
    action: Optional[str] = None
    model_type: Optional[str] = None
    target_id: Optional[int] = None


class LogEntryPublicSchema(IDSchemaMixin, CreatedAtSchemaMixin, LogEntryBaseSchema):
    pass


class LogEntryCreateSchema(CoreSchema):
    user_id: Optional[int] = None
    action: Optional[str] = None
    model_type: Optional[str] = None
    target_id: Optional[int] = None
