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

    @field_validator("created_at")
    def parse_created_at(cls, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")


    @field_validator('created_at', 'updated_at')
    def default_created_at(cls, value: datetime) -> datetime:
        return value or datetime.now()

    @field_validator("updated_at")
    def parse_updated_at(cls, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")


class SuccessResponseScheme(BaseModel):
    message: str
