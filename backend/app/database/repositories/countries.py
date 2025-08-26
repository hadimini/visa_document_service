from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.countries import Country
from app.schemas.country import CountryFilterSchema, CountryUpdateSchema
from app.schemas.pagination import PageParamsSchema


class CountriesRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.db = db

    async def get_list(self, *, filters: CountryFilterSchema, page_params: PageParamsSchema):
        statement = select(Country).order_by(Country.id)

        if filters.name:
            statement = statement.filter(Country.name.ilike(f"%{filters.name}%"))

        paginated_query = statement.offset((page_params.page - 1) * page_params.size).limit(page_params.size)
        results = await self.db.execute(paginated_query)
        return results.scalars().all()

    async def get_by_id(self, *, country_id: int):
        statement = select(Country).where(Country.id == country_id)
        result = await self.db.execute(statement)
        country = result.one_or_none()
        return country[0] if country else None

    async def update(self, *, country_id: int, data: CountryUpdateSchema) -> Country | None:
        country = await self.get_by_id(country_id=country_id)

        if country:
            for key, item in data.model_dump().items():
                setattr(country, key, item)
            await self.db.commit()
            return country
