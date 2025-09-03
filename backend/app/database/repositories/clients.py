from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.database.repositories.users import UsersRepository
from app.models.clients import Client
from app.schemas.client import ClientCreateSchema, ClientFilterSchema
from app.schemas.pagination import PageParamsSchema


class ClientRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.users_repo = UsersRepository(db)

    async def get_list(self, *, filters: ClientFilterSchema, page_params: PageParamsSchema) -> Sequence[Client]:
        statement = select(Client).options(selectinload(Client.tariff))

        if filters.name:
            statement = statement.where(Client.name.ilike(f"%{filters.name}%"))

        if filters.type:
            statement = statement.where(Client.type == filters.type)
        paginated_query = statement.offset((page_params.page - 1) * page_params.size).limit(page_params.size)

        result = await self.db.scalars(paginated_query)
        return result.all()

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
