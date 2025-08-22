from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.tariffs import Tariff
from app.schemas.tariff import TariffCreateSchema


class TariffsRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_default(self) -> Tariff:
        statement = select(Tariff).where(Tariff.is_default == True)
        result = await self.db.execute(statement)
        tariff = result.one_or_none()
        return tariff[0] if tariff else None

    async def create(self, *, new_tariff: TariffCreateSchema) -> Tariff:
        new_tariff = Tariff(**new_tariff.model_dump())
        self.db.add(new_tariff)
        await self.db.commit()
        return new_tariff
