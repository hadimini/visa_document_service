from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ClauseElement

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.models import Service, TariffService
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
        """Get service by id with relations loaded"""
        options = [selectinload(Service.tariff_services).selectinload(TariffService.tariff)]
        statement = select(Service).options(*options).where(Service.id == service_id)
        result = await self.db.scalars(statement)
        service = result.unique().one_or_none()
        return service

    async def create(self, *, data: ServiceCreateSchema) -> Service:
        service_data = data.model_dump(exclude={"tariff_services"})
        service = Service(**service_data)
        self.db.add(service)
        await self.db.flush()  # Flush to get the service ID

        # Create tariff services if provided
        if data.tariff_services:
            for tariff_service_data in data.tariff_services:
                tariff_service = TariffService(
                    service_id=service.id,
                    **tariff_service_data.model_dump()
                )
                self.db.add(tariff_service)

        await self.db.commit()
        return await self.get_by_id(service_id=service.id)
