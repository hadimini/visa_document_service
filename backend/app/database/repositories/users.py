from typing import Any

from pydantic import EmailStr
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ClauseElement

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.exceptions import AuthEmailAlreadyRegisteredException, AuthEmailAlreadyVerifiedException, NotFoundException
from app.models.users import User
from app.schemas.pagination import PageParamsSchema
from app.schemas.user import (
    UserCreateSchema,
    UserCreateInDBSchema,
    UserUpdateSchema,
    UserFilterSchema
)
from app.services.auth import AuthService


class UsersRepository(BasePaginatedRepository, BuildFiltersMixin):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db=db, model=User)
        self.auth_service = AuthService()

    def build_filters(self, *, query_filters: UserFilterSchema) -> list:
        filters: list[ClauseElement] = list()

        if query_filters.name:
            filters.append(
                or_(
                    User.first_name.ilike(f"%{query_filters.name}%"),
                    User.last_name.ilike(f"%{query_filters.name}%"),
                )
            )

        if query_filters.role:
            filters.append(User.role == query_filters.role)
        #     TODO: compare to below
        # if query_filters.name:
        #     statement = statement.filter(
        #         or_(
        #             User.first_name.ilike(f"%{query_filters.name}%"),
        #             User.last_name.ilike(f"%{query_filters.name}%"),
        #         )
        #     )
        # if query_filters.role:
        #     statement = statement.filter(
        #         User.role == query_filters.role
        #     )

        return filters

    async def get_list(self, *, query_filters: UserFilterSchema, page_params: PageParamsSchema) -> dict[str, Any]:
        statement = select(User)
        filters = self.build_filters(query_filters=query_filters)

        if filters:
            statement = statement.filter(*filters)

        return await self.paginate(statement, page_params=page_params)

    async def get_by_id(self, *, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = await self.db.scalars(statement)
        return result.one_or_none()

    async def create(self, *, new_user: UserCreateSchema) -> User | None:
        if await self.get_by_email(email=new_user.email):
            raise AuthEmailAlreadyRegisteredException(email=new_user.email)

        user_password_update = self.auth_service.create_salt_and_hashed_password(
            plaintext_password=new_user.password
        )
        new_user = UserCreateInDBSchema(
            **new_user.model_dump(exclude={"password"}),
            **user_password_update.model_dump()
        )
        user = User(**new_user.model_dump())
        self.db.add(user)
        await self.db.commit()
        return user

    async def update(self, *, user: User, data: UserUpdateSchema) -> User | None:
        statement = update(User).where(User.id == user.id).values(
            **data.model_dump()
        )
        await self.db.execute(statement)
        await self.db.commit()
        updated_user = await self.get_by_id(user_id=user.id)
        return updated_user

    async def get_by_email(self, *, email: EmailStr) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        user = result.one_or_none()
        return user[0] if user else None

    async def authenticate(self, *, email: EmailStr, password: str) -> User | None:
        user = await self.get_by_email(email=email)

        if not user:
            return None

        if not self.auth_service.verify_password(
                password=password,
                salt=user.salt,
                hashed_password=user.password
        ):
            return None

        return user

    async def verify_email(self, *, user_id: int) -> None:
        user = await self.get_by_id(user_id=user_id)

        if not user:
            raise NotFoundException()

        if user.email_verified:
            raise AuthEmailAlreadyVerifiedException()

        user.email_verified = True
        await self.db.commit()
