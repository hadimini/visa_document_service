from datetime import datetime

from pydantic import BaseModel, field_validator


STRFTIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class CoreSchema(BaseModel):
    class Config:
        # arbitrary_types_allowed = True
        from_attributes = True


class IDSchemaMixin(BaseModel):
    id: int


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


class DateTimeSchemaMixin(CreatedAtSchemaMixin, UpdatedAtSchemaMixin):
    pass


class SuccessResponseScheme(BaseModel):
    message: str
