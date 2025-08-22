from fastapi import Query
from typing import Annotated, Literal, Optional
from pydantic import EmailStr, StringConstraints

from app.models.users import User
from app.schemas.core import CoreSchema, IDSchemaMixin, DateTimeSchemaMixin


class UserBaseSchema(CoreSchema):
    email: Optional[EmailStr]
    email_verified: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    role: Literal["admin", "employee", "individual", "manager", "operator"] | None = User.ROLE_INDIVIDUAL


class UserCreateSchema(CoreSchema):
    email: EmailStr
    first_name: Annotated[str, StringConstraints(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")]
    last_name: Annotated[str, StringConstraints(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")]
    password: Annotated[str, StringConstraints(min_length=5, max_length=100)]
    role: Literal["admin", "employee", "individual", "manager", "operator"] | None = None
    employee_client_id: Optional[int] = None
    individual_client_id: Optional[int] = None
    manager_client_id: Optional[int] = None


class UserCreateInDBSchema(UserCreateSchema):
    salt: str


class UserUpdateSchema(CoreSchema):
    first_name: str
    last_name: str


class UserPublicSchema(IDSchemaMixin, DateTimeSchemaMixin, UserBaseSchema):
    pass


class UserPasswordUpdateSchema(CoreSchema):
    password: str
    salt: str


class UserFilterSchema(CoreSchema):
    name: Annotated[str | None, Query(max_length=50, description="Filter by user's name")] = None
    role: Literal["admin", "employee", "individual", "manager", "operator"] | None = None
