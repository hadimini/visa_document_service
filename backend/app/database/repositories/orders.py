from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.elements import ClauseElement

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin

from app.models import Order
from app.schemas.order.base import OrdersFilterSchema


class OrdersRepository(BasePaginatedRepository[Order], BuildFiltersMixin):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db=db, model=Order)

    def build_filters(self, *, query_filters: OrdersFilterSchema) -> list:
        """Convert filter schema to SQLAlchemy filter conditions"""
        filters: list[ClauseElement] = list()

        for attr in {
            "status", "country_id", "client_id", "created_by_id", "urgency_id", "visa_duration_id", "visa_type_id"
        }:
            value = getattr(query_filters, attr)

            if value is not None:
                filters.append(
                    getattr(self.model, attr) == value
                )

        return filters

    async def get_by_id(self, *, order_id: int, populate_client: Optional[bool] = False) -> Order | None:
        options = [joinedload(Order.client)]

        statement = select(Order)

        if populate_client:
            statement = statement.options(*options)

        result = await self.db.scalars(statement.where(Order.id == order_id))
        return result.one_or_none()

    # TODO: Create
    # TODO: Update
