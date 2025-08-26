from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.countries import Country
from app.schemas.country import CountryFilterSchema
from app.schemas.pagination import PageParamsSchema


class CountriesRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.db = db

    async def get_all(self, *, filters: CountryFilterSchema, page_params: PageParamsSchema):
        statement = select(Country).order_by(Country.id)

        if filters.name:
            statement = statement.filter(Country.name.ilike(f"%{filters.name}%"))

        paginated_query = statement.offset((page_params.page - 1) * page_params.size).limit(page_params.size)

        results = await self.db.execute(paginated_query)
        return results.scalars().all()
