from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql.elements import ClauseElement

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.database.repositories.users import UsersRepository
from app.models.clients import Client
from app.schemas.client import ClientCreateSchema, ClientFilterSchema
from app.schemas.pagination import PageParamsSchema


class ClientsRepository(BasePaginatedRepository[Client], BuildFiltersMixin):
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

    async def get_paginated_list(
            self,
            *,
            query_filters: Optional[ClientFilterSchema] = None,
            page_params: PageParamsSchema
    ) -> dict[str, Any]:
        return await super().get_paginated_list(
            query_filters=query_filters,
            page_params=page_params,
            options=[selectinload(Client.tariff)]
        )

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
