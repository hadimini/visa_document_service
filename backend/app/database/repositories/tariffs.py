from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.tariffs import Tariff
from app.schemas.tariff import TariffCreateSchema


class TariffsRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_default(self) -> Tariff | None:
        statement = select(Tariff).where(Tariff.is_default.is_(True))
        result = await self.db.scalars(statement)
        return result.one_or_none()

    async def create(self, *, new_tariff: TariffCreateSchema) -> Tariff:
        tariff = Tariff(**new_tariff.model_dump())
        self.db.add(tariff)
        await self.db.commit()
        return tariff
