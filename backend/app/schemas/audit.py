from typing import Optional

from app.schemas.core import CoreSchema, CreatedAtSchemaMixin, IDSchemaMixin


class EntryLogBaseSchema(CoreSchema):
    user_id: Optional[int] = None
    action: Optional[str] = ""
    model_type: Optional[str] = ""


class EntryLogPublicSchema(IDSchemaMixin, CreatedAtSchemaMixin, EntryLogBaseSchema):
    pass


class EntryLogCreateSchema(EntryLogBaseSchema):
    action: str
