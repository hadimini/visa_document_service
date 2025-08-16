from typing import Optional
from pydantic import EmailStr, constr

from app.schemas.core import CoreSchema, IDSchemaMixin, DateTimeSchemaMixin


class UserBaseScheme(CoreSchema):
    email: Optional[EmailStr]
    email_verified: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True


class UserCreateScheme(CoreSchema):
    email: EmailStr
    first_name: constr(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")
    last_name: constr(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")
    password: constr(min_length=5, max_length=100)


class UserCreateInDBScheme(UserCreateScheme):
    salt: str


class UserPublicScheme(IDSchemaMixin, DateTimeSchemaMixin, UserBaseScheme):
    pass


class UserPasswordUpdate(CoreSchema):
    password: str
    salt: str
