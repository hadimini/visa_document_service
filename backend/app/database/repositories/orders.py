import logging

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.elements import ClauseElement

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.models import Order, Applicant
from app.schemas.order.admin import AdminOrderCreateSchema, AdminOrderUpdateSchema
from app.schemas.order.admin import AdminOrderFilterSchema

logger = logging.getLogger(__name__)


class OrdersRepository(BasePaginatedRepository[Order], BuildFiltersMixin):
    """Repository for managing orders in the database.

    This class provides methods to create, update, retrieve, and filter orders.

    Attributes:
        db (AsyncSession): The asynchronous database session used for operations.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the OrdersRepository with a database session.

        Args:
            db (AsyncSession): The asynchronous database session.
        """
        super().__init__(db=db, model=Order)

    def build_filters(self, *, query_filters: AdminOrderFilterSchema) -> list:
        """Convert filter schema to SQLAlchemy filter conditions.

        This method constructs a list of filter conditions based on the provided
        AdminOrderFilterSchema.

        Args:
            query_filters (AdminOrderFilterSchema): The filter schema containing the attributes to filter by.

        Returns:
            list: A list of SQLAlchemy filter conditions.
        """

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
        """Retrieve an order by its ID.

        This method fetches an order from the database, optionally populating
        the associated client data.

        Args:
            order_id (int): The ID of the order to retrieve.
            populate_client (Optional[bool]): Whether to include client data in
                the result. Defaults to False.

        Returns:
            Order | None: The retrieved order, or None if not found.
        """
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
        """Create a new order in the database.

        This method adds a new order based on the provided data schema and
        commits it to the database.

        Args:
            data (AdminOrderCreateSchema): The data schema containing order
                details.
            populate_client (bool): Whether to include client data in the
                returned order. Defaults to False.

        Returns:
            Order: The created order instance.

        Raises:
            Exception: If the order creation fails.
        """
        # TODO: assert country.available_for_order is True

        try:
            order = Order(**data.model_dump())
            self.db.add(order)
            await self.db.commit()
            order = await self.get_by_id(order_id=order.id, populate_client=populate_client)
            return order
        except Exception as e:
            logger.error(f"Failed to create order: {str(e)}")
            await self.db.rollback()
            raise e

    async def update(
            self,
            *,
            order_id: int,
            data: AdminOrderUpdateSchema,
            populate_client: bool = False
    ) -> Order | None:
        """Update an existing order in the database.

        This method modifies an existing order based on the provided data
        schema and commits the changes to the database.

        Args:
            order_id (int): The ID of the order to update.
            data (AdminOrderUpdateSchema): The data schema containing updated
                order details.
            populate_client (bool): Whether to include client data in the
                returned order. Defaults to False.

        Returns:
            Order | None: The updated order instance, or None if not
        """

        try:
            order = await self.get_by_id(order_id=order_id)

            if not order:
                return None

            order_data = data.model_dump(exclude_unset=True, exclude={"applicant"})

            for attr, value in order_data.items():
                setattr(order, attr, value)

            if data.applicant:
                if order.applicant:
                    # Update existing applicant
                    applicant_data = data.applicant.model_dump(exclude_unset=True)
                    for attr, value in applicant_data.items():
                        setattr(order.applicant, attr, value)
                else:
                    # Create new applicant
                    applicant_data = data.applicant.model_dump()
                    applicant = Applicant(**applicant_data, order_id=order.id)
                    self.db.add(applicant)

            await self.db.commit()
            await self.db.refresh(order)

            order = await self.get_by_id(order_id=order.id, populate_client=populate_client)
            return order

        except Exception as e:
            logger.error(f"Failed to create order: {str(e)}")
            await self.db.rollback()
            raise e
