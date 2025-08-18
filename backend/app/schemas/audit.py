from typing import Optional

from app.schemas.core import CoreSchema, CreatedAtSchemaMixin, IDSchemaMixin


class LogEntryBaseSchema(CoreSchema):
    user_id: Optional[int] = None
    action: Optional[str] = ""
    model_type: Optional[str] = ""


class LogEntryPublicSchema(IDSchemaMixin, CreatedAtSchemaMixin, LogEntryBaseSchema):
    pass


class LogEntryCreateSchema(LogEntryBaseSchema):
    action: str
