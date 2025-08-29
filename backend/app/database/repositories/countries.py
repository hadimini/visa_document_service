from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from app.database.repositories.base import BaseRepository
from app.models import CountryVisa
from app.models.countries import Country
from app.schemas.country import CountryFilterSchema, CountryUpdateSchema
from app.schemas.pagination import PageParamsSchema


class CountriesRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.db = db

    async def get_list(self, *, filters: CountryFilterSchema, page_params: PageParamsSchema):
        # First, get paginated country IDs
        count_stmt = select(Country.id)
        if filters.name:
            count_stmt = count_stmt.filter(Country.name.ilike(f"%{filters.name}%"))

        count_stmt = count_stmt.offset((page_params.page - 1) * page_params.size).limit(page_params.size)
        country_ids = (await self.db.scalars(count_stmt)).all()

        # Then fetch countries with relationships
        if country_ids:
            statement = select(Country).options(
                selectinload(Country.country_visas).selectinload(CountryVisa.visa_type)
            ).where(Country.id.in_(country_ids)).order_by(Country.id)

            result = await self.db.scalars(statement)
            return result.unique().all()
        else:
            return []

    async def get_by_id(self, *, country_id: int):
        statement = select(Country).options(
            joinedload(Country.country_visas).joinedload(CountryVisa.visa_type),
        ).where(Country.id == country_id)

        result = await self.db.scalars(statement)
        return result.unique().one_or_none()

    async def update(self, *, country_id: int, data: CountryUpdateSchema) -> Country | None:
        await self.db.execute(
            update(Country)
            .where(Country.id == country_id)
            .values(**data.model_dump())
        )
        await self.db.commit()

        country = await self.get_by_id(country_id=country_id)
        return country
