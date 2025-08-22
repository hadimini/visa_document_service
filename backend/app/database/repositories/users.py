from pydantic import EmailStr
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.exceptions import AuthEmailAlreadyRegisteredException
from app.models.users import User
from app.schemas.pagination import PageParamsSchema
from app.schemas.user import (
    UserCreateSchema,
    UserCreateInDBSchema,
    UserUpdateSchema,
    UserFilterSchema
)
from app.services.auth import AuthService


class UsersRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.auth_service = AuthService()

    async def create(self, *, new_user: UserCreateSchema) -> User:
        if await self.get_by_email(email=new_user.email):
            raise AuthEmailAlreadyRegisteredException(email=new_user.email)

        user_password_update = self.auth_service.create_salt_and_hashed_password(
            plaintext_password=new_user.password
        )
        new_user = UserCreateInDBSchema(
            **new_user.model_dump(exclude={"password"}),
            **user_password_update.model_dump()
        )
        new_user = User(**new_user.model_dump())
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update(self, *, user: User, data: UserUpdateSchema) -> User:
        statement = update(User).where(User.id == user.id).values(
            **data.model_dump()
        )
        await self.db.execute(statement)
        await self.db.commit()
        updated_user = await self.get_by_id(user_id=user.id)
        return updated_user

    async def get_all(self, *, filters: UserFilterSchema, page_params: PageParamsSchema):
        statement = select(User)
        if filters.name:
            statement = statement.filter(
                or_(
                    User.first_name.ilike(f"%{filters.name}%"),
                    User.last_name.ilike(f"%{filters.name}%"),
                )
            )
        if filters.role:
            statement = statement.filter(
                User.role == filters.role
            )

        paginated_query = statement.offset((page_params.page - 1) * page_params.size).limit(page_params.size)
        result = await self.db.execute(paginated_query)
        users = result.scalars().all()
        return users

    async def get_by_id(self, *, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = await self.db.execute(statement)
        user = result.one_or_none()
        return user[0] if user else None

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
