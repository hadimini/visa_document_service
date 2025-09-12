from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

STRFTIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class CoreSchema(BaseModel):
    class Config:
        from_attributes = True


class IDSchemaMixin(BaseModel):
    id: int


class ArchivedAtSchemaMixin(BaseModel):
    archived_at: Optional[datetime] = None

    @field_validator("archived_at")
    def parse_archived_at(cls, value: datetime | None) -> str | None:
        return value.strftime(STRFTIME_FORMAT) if value else None


class CreatedAtSchemaMixin(BaseModel):
    created_at: datetime

    @field_validator("created_at")
    def parse_created_at(cls, value: datetime) -> str:
        return value.strftime(STRFTIME_FORMAT)

    @field_validator('created_at')
    def default_created_at(cls, value: datetime) -> datetime:
        return value or datetime.now()


class UpdatedAtSchemaMixin(BaseModel):
    updated_at: datetime

    @field_validator("updated_at")
    def parse_updated_at(cls, value: datetime) -> str:
        return value.strftime(STRFTIME_FORMAT)

    @field_validator('updated_at')
    def default_updated_at(cls, value: datetime) -> datetime:
        return value or datetime.now()


class CompletedAtSchemaMixin(BaseModel):
    completed_at: Optional[datetime] = None

    @field_validator("completed_at")
    def parse_completed_at(cls, value: datetime | None) -> str:
        return value and value.strftime(STRFTIME_FORMAT)

    @field_validator('completed_at')
    def default_completed_at(cls, value: datetime | None) -> datetime:
        return value


class DateTimeSchemaMixin(CreatedAtSchemaMixin, UpdatedAtSchemaMixin):
    pass
