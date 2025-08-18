from typing import Optional
from pydantic import EmailStr, constr, field_serializer
from sqlalchemy_utils import Choice

from app.models.users import User
from app.schemas.core import CoreSchema, IDSchemaMixin, DateTimeSchemaMixin


class UserBaseSchema(CoreSchema):
    email: Optional[EmailStr]
    email_verified: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    role: Optional[Choice] = User.ROLE_USER

    @field_serializer("role")
    def serialize_role(self, value) -> str:
        return value.code


class UserCreateSchema(CoreSchema):
    email: EmailStr
    first_name: constr(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")
    last_name: constr(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9 ]+$")
    password: constr(min_length=5, max_length=100)


class UserCreateInDBSchema(UserCreateSchema):
    salt: str


class UserPublicSchema(IDSchemaMixin, DateTimeSchemaMixin, UserBaseSchema):
    pass


class UserPasswordUpdateSchema(CoreSchema):
    password: str
    salt: str
