from typing import Any

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.database.repositories.users import UsersRepository
from app.models.clients import Client
from app.schemas.client import ClientCreateSchema, ClientFilterSchema
from app.schemas.pagination import PageParamsSchema


class ClientRepository(BasePaginatedRepository, BuildFiltersMixin):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db=db, model=Client)
        self.users_repo = UsersRepository(db)

    def build_filters(self, *, query_filters: ClientFilterSchema) -> list:
        """Convert filter schema to SQLAlchemy filter conditions"""
        filters: list[ClauseElement] = list()

        if query_filters.name:
            filters.append(Client.name.ilike(f"%{query_filters.name}%"))

        if query_filters.type:
            filters.append(Client.type == query_filters.type)
        return filters

    async def get_list(self, *, query_filters: ClientFilterSchema, page_params: PageParamsSchema) -> dict[str, Any]:
        statement = select(Client).options(selectinload(Client.tariff))
        filters = self.build_filters(query_filters=query_filters)

        if filters:
            statement = statement.where(and_(*filters))

        return await self.paginate(statement, page_params)

    async def get_by_id(self, *, client_id: int) -> Client | None:
        statement = select(Client).options(
            joinedload(Client.tariff)
        ).where(Client.id == client_id)
        result = await self.db.scalars(statement)
        return result.unique().one_or_none()

    async def create(self, *, new_client: ClientCreateSchema) -> Client:
        data: dict = {
            "name": new_client.name,
            "tariff_id": new_client.tariff_id,
            "type": Client.TYPE_INDIVIDUAL
        }

        client = Client(**data)
        self.db.add(client)
        await self.db.commit()
        return client
