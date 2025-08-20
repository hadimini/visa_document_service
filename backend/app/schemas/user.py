from fastapi import Query
from typing import Annotated, Optional
from pydantic import EmailStr, StringConstraints

from app.models.users import User
from app.schemas.core import CoreSchema, IDSchemaMixin, DateTimeSchemaMixin


class UserBaseSchema(CoreSchema):
    email: Optional[EmailStr]
    email_verified: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    role: Optional[str] = User.ROLE_USER


class UserCreateSchema(CoreSchema):
    email: EmailStr
    first_name: Annotated[str, StringConstraints(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")]
    last_name: Annotated[str, StringConstraints(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")]
    password: Annotated[str, StringConstraints(min_length=5, max_length=100)]
    role: Optional[str] = User.ROLE_USER


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
    name: str | None = Query(None, description="Filter by user's name")
    role: str | None = Query(None, description="Filter by user's role")
