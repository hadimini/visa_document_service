from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.database.repositories.users import UsersRepository
from app.models.clients import Client
from app.schemas.client import ClientCreateSchema


class ClientRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.users_repo = UsersRepository(db)

    async def get_by_id(self, *, client_id: int) -> Client:
        statement = select(Client).where(Client.id == client_id)
        result = await self.db.execute(statement)
        client = result.one_or_none()
        return client[0] if client else None

    async def create(self, *, new_client: ClientCreateSchema):
        data: dict = {
            "name": new_client.name,
            "tariff_id": new_client.tariff_id,
            "type": Client.TYPE_INDIVIDUAL
        }

        client = Client(**data)
        self.db.add(client)
        await self.db.commit()
        return client
