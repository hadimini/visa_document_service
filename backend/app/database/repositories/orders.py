from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.elements import ClauseElement

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.models import Order, Applicant
from app.schemas.order.admin import AdminOrderCreateSchema, AdminOrderUpdateSchema
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

    async def get_by_id(
            self,
            *,
            order_id: int,
            populate_client: Optional[bool] = False
    ) -> Order | None:
        options = [
            joinedload(Order.country),
            joinedload(Order.created_by),
            joinedload(Order.urgency),
            joinedload(Order.visa_type),
            joinedload(Order.visa_duration),
            joinedload(Order.applicant),
        ]
        statement = select(Order)

        if populate_client:
            options.append(joinedload(Order.client))

        statement = statement.options(*options).where(Order.id == order_id)
        result = await self.db.execute(statement)
        return result.scalars().one_or_none()

    async def create(self, *, data: AdminOrderCreateSchema, populate_client: bool = False) -> Order:
        try:
            # Create the order without the applicant field
            order = Order(**data.model_dump(exclude_unset=True, exclude={"applicant"}))
            self.db.add(order)
            await self.db.flush()

            # If there's applicant data, create the applicant
            if data.applicant:
                applicant_data = data.applicant.model_dump()
                applicant = Applicant(**applicant_data, order_id=order.id)
                self.db.add(applicant)

            await self.db.commit()
            order = await self.get_by_id(order_id=order.id, populate_client=populate_client)
            return order
        except Exception as e:
            await self.db.rollback()
            raise e

    async def update(
            self,
            *,
            order_id: int,
            data: AdminOrderUpdateSchema,
            populate_client: bool = False
    ) -> Order | None:
        try:
            order = await self.get_by_id(order_id=order_id)

            if not order:
                return None

            order_data = data.model_dump(exclude_unset=True, exclude={"applicant"})

            for attr, value in order_data.items():
                setattr(order, attr, value)

            if data.applicant:
                statement = update(Applicant).where(Applicant.order_id == order_id).values(
                    **data.applicant.model_dump(exclude_unset=True)
                )
                await self.db.execute(statement)

            await self.db.commit()

            order = await self.get_by_id(order_id=order.id, populate_client=populate_client)
            return order

        except Exception as e:
            await self.db.rollback()
            raise e
