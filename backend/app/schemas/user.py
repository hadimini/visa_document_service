from fastapi import Query
from typing import Annotated, Literal, Optional
from pydantic import EmailStr, Field, StringConstraints

from app.models import User
from app.schemas.core import CoreSchema, IDSchemaMixin, DateTimeSchemaMixin
from app.schemas.pagination import PagedResponseSchema


class UserBaseSchema(CoreSchema):
    MODEL_TYPE: str = Field(default_factory=lambda: User.get_model_type())
    email: Optional[EmailStr]
    email_verified: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    role: Literal["admin", "employee", "individual", "manager", "operator"] | None = None  # type: ignore[arg-type]


class UserCreateSchema(CoreSchema):
    email: EmailStr
    first_name: Annotated[str, StringConstraints(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")]
    last_name: Annotated[str, StringConstraints(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")]
    password: Annotated[str, StringConstraints(min_length=5, max_length=100)]
    role: Literal["admin", "employee", "individual", "manager", "operator"] | None = None
    employee_client_id: Optional[int] = None
    individual_client_id: Optional[int] = None
    manager_client_id: Optional[int] = None

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class UserCreateInDBSchema(UserCreateSchema):
    salt: str


class UserUpdateSchema(CoreSchema):
    first_name: str
    last_name: str


class UserResponseSchema(IDSchemaMixin, DateTimeSchemaMixin, UserBaseSchema):
    pass


class UserPasswordUpdateSchema(CoreSchema):
    password: str
    salt: str


class UserFilterSchema(CoreSchema):
    name: Annotated[str | None, Query(max_length=50, description="Filter by user's name")] = None
    role: Literal["admin", "employee", "individual", "manager", "operator"] | None = None


class UserListResponseSchema(PagedResponseSchema, CoreSchema):
    items: list[UserResponseSchema]
