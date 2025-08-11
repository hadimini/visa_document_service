from datetime import datetime

from pydantic import BaseModel, field_validator


class CoreModel(BaseModel):
    class Config:
        from_attributes = True


class IDModelMixin(BaseModel):
    id: int


class DateTimeModelMixin(BaseModel):
    created_at: datetime
    updated_at: datetime

    @field_validator('created_at', 'updated_at')
    def default_created_at(cls, value: datetime) -> datetime:
        return value or datetime.now()
