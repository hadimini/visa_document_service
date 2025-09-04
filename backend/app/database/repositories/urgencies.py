from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.urgencies import Urgency
from app.exceptions import NameExistsException, NotFoundException
from app.schemas.urgency import UrgencyCreateSchema, UrgencyUpdateSchema


class UrgenciesRepository(BaseRepository):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.db = db

    async def get_list(self) -> Sequence[Urgency]:
        statement = select(Urgency).order_by(Urgency.id)
        result = await self.db.scalars(statement)
        return result.all()

    async def get_by_id(self, *, urgency_id: int) -> Urgency | None:
        statement = select(Urgency).where(Urgency.id == urgency_id)
        result = await self.db.execute(statement)
        urgency = result.scalars().one_or_none()
        return urgency

    async def get_by_name(self, *, name: str) -> Urgency | None:
        statement = select(Urgency).where(Urgency.name == name)
        result = await self.db.scalars(statement)
        return result.one_or_none()

    async def create(self, *, data: UrgencyCreateSchema) -> Urgency:
        urgency = Urgency(**data.model_dump())

        if await self.get_by_name(name=urgency.name) is not None:
            raise NameExistsException()

        self.db.add(urgency)
        await self.db.commit()
        return urgency

    async def update(self, *, urgency_id: int, data: UrgencyUpdateSchema) -> Urgency | None:
        urgency = await self.get_by_id(urgency_id=urgency_id)

        if not urgency:
            raise NotFoundException()

        for attr, value in data.model_dump().items():
            setattr(urgency, attr, value)
            await self.db.commit()
            await self.db.refresh(urgency)
        return urgency
