from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ClauseElement

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.models import Service
from app.schemas.service import ServiceCreateSchema, ServiceFilterSchema


class ServicesRepository(BasePaginatedRepository[Service], BuildFiltersMixin):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db=db, model=Service)

    def build_filters(self, *, query_filters: ServiceFilterSchema) -> list:
        """Convert filter schema to SQLAlchemy filter conditions"""
        filters: list[ClauseElement] = list()

        if query_filters.name:
            filters.append(Service.name.ilike(f"%{query_filters.name}%"))

        if query_filters.fee_type:
            filters.append(Service.fee_type == query_filters.fee_type)
            # filters.append(Service.fee_type == query_filters.fee_type.value)

        if query_filters.country_id:
            filters.append(Service.country_id == query_filters.country_id)

        if query_filters.urgency_id:
            filters.append(Service.urgency_id == query_filters.urgency_id)

        if query_filters.visa_duration_id:
            filters.append(Service.visa_duration_id == query_filters.visa_duration_id)

        if query_filters.visa_type_id:
            filters.append(Service.visa_type_id == query_filters.visa_type_id)

        return filters

    async def get_by_id(self, *, service_id) -> Service | None:
        # options = [joinedload(Service.tariff)]  # todo

        statement = select(Service).where(Service.id == service_id)
        return (
            await self.db.scalars(statement)
        ).one_or_none()

    async def create(self, *, data: ServiceCreateSchema) -> Service:
        service = Service(**data.model_dump())
        self.db.add(service)
        await self.db.commit()
        return service
