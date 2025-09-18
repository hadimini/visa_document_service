import logging
from typing import Sequence, Optional

from sqlalchemy import delete, select, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from app.database.repositories.base import BaseRepository
from app.models import Client, Order, OrderService, Service, TariffService
from app.schemas.order_service import OrderServicesUpdateSchema

logger = logging.getLogger(__name__)


class OrderServicesRepository(BaseRepository):
    """
    Repository for managing order services operations.

    Handles retrieval of available services for orders and updating order service assignments.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the repository with a database session.

        Args:
            db: Async database session
        """
        super().__init__(db)

    async def get_for_order(self, *, order_id: int) -> dict[str, Sequence | None]:
        """
        Retrieve all services for a specific order, including attached and available services.

        This method fetches:
        - Services already attached to the order
        - Services available for attachment based on order criteria and client's tariff

        Args:
            order_id: ID of the order to retrieve services for

        Returns:
            Dictionary with two keys:
            - 'attached': List of OrderService objects currently attached to the order
            - 'available': List of available services with tariff pricing information

        Raises:
            ValueError: If order is not found or client has no tariff assigned
            Exception: If database operation fails
        """
        try:
            stmt = (
                select(
                    Order.country_id,
                    Order.urgency_id,
                    Order.visa_duration_id,
                    Order.visa_type_id,
                    Client.tariff_id,
                )
                .join(Client, Client.id == Order.client_id)
                .where(Order.id == order_id)
            )
            row = (await self.db.execute(stmt)).one_or_none()

            if row is None:
                raise ValueError("order not found")

            country_id, urgency_id, visa_duration_id, visa_type_id, tariff_id = row

            if tariff_id is None:
                raise ValueError("client has no tariff; cannot create or modify order")

            # attached services unchanged
            attached_statement = (
                select(OrderService)
                .options(selectinload(OrderService.service))
                .join(OrderService.service)
                .where(OrderService.order_id == order_id)
                .order_by(Service.name)
            )
            attached_services = (await self.db.execute(attached_statement)).scalars().all()
            attached_ids = (
                select(OrderService.service_id)
                .where(OrderService.order_id == order_id)
                .subquery()
            )

            TS = aliased(TariffService)
            available_statement = (
                select(Service, TS)
                .join(TS, and_(TS.service_id == Service.id, TS.tariff_id == tariff_id))
                .where(~Service.id.in_(attached_ids))
            )

            def add_value_or_none(col, value):
                nonlocal available_statement
                available_statement = (
                    available_statement.where(col.is_(None))
                    if value is None
                    else available_statement.where(or_(col.is_(None), col == value))
                )

            add_value_or_none(Service.country_id, country_id)
            add_value_or_none(Service.urgency_id, urgency_id)
            add_value_or_none(Service.visa_duration_id, visa_duration_id)
            add_value_or_none(Service.visa_type_id, visa_type_id)

            available_statement = available_statement.order_by(Service.name)
            rows = (await self.db.execute(available_statement)).all()

            available_services = [
                {
                    "service": service,
                    "id": getattr(ts, "id", None),
                    "price": getattr(ts, "price", None),
                    "tax": getattr(ts, "tax", None),
                    "tax_amount": getattr(ts, "tax_amount", None),
                    "total": getattr(ts, "total", None),
                }
                for service, ts in rows
            ]

            return {"attached": attached_services, "available": available_services}
        except SQLAlchemyError as e:
            logger.error(f"Failed to get services for order: {str(e)}")
            await self.db.rollback()
            raise Exception(f"Failed to get services for order: {str(e)}") from e

    async def update_for_order(self, *, order_id: int, data: OrderServicesUpdateSchema) -> None:
        """
        Update services for a specific order.

        Replaces all existing services attached to the order with new services
        specified by tariff service IDs. Fetches pricing information from the
        tariff services to create proper OrderService records with calculated taxes.

        Args:
            order_id: ID of the order to update services for
            data: Schema containing tariff_services_ids to attach to the order

        Raises:
            Exception: If database operation fails

        Note:
            - If tariff_services_ids is None, no action is taken
            - If tariff_services_ids is empty list, all services are removed from the order
            - Tax amounts and totals are automatically calculated during OrderService creation
        """
        try:
            tariff_services_ids: Optional[list[int]] = data.tariff_services_ids

            if tariff_services_ids is not None:
                delete_stmt = delete(OrderService).where(OrderService.order_id == order_id)
                await self.db.execute(delete_stmt)

                if tariff_services_ids:
                    services_stmt = select(
                        TariffService.price,
                        TariffService.tax,
                        TariffService.service_id
                    ).where(TariffService.id.in_(tariff_services_ids))
                    rows = (await self.db.execute(services_stmt)).all()

                    if not rows:
                        logger.warning(f"No tariff services found for IDs: {tariff_services_ids}")
                        await self.db.commit()
                        return

                    order_services_data = []

                    for price, tax, service_id in rows:
                        order_services_data.append(
                            OrderService(price=price, tax=tax, order_id=order_id, service_id=service_id)
                        )
                    self.db.add_all(order_services_data)

                await self.db.commit()
        except SQLAlchemyError as e:
            logger.error(f"Failed to update services for order: {str(e)}")
            await self.db.rollback()
            raise Exception(f"Failed to update services for order: {str(e)}") from e
