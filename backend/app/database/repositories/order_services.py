from typing import Sequence

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from app.database.repositories.base import BaseRepository
from app.models import Client, Order, OrderService, Service, TariffService


class OrderServicesRepository(BaseRepository):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_for_order(self, *, order_id: int) -> dict[str, Sequence | None]:
        """
        Retrieve services for an order.

        Returns a dict with:

        "attached": list[OrderService] — OrderService ORM instances already attached to the order (their Service is eager-loaded).
        "available": list[dict] — services not attached to the order that have a TariffService for the client's tariff. Each dict contains:
        "service": Service ORM instance
        "id": TariffService.id
        "price": TariffService.price
        "tax": TariffService.tax
        "tax_amount": TariffService.tax_amount
        "total": TariffService.total
        Behavior and constraints:

        Fetches Order fields and Client.tariff_id in one query; raises ValueError("order not found") if the order does not exist.
        Raises ValueError("client has no tariff; cannot create or modify order") if the client has no tariff_id.
        "attached" is populated by selecting OrderService rows for the order with Service eagerly loaded to avoid N+1 queries.
        "available" uses an INNER JOIN between services and tariff_services filtered by the client's tariff_id,
        so only services that have a TariffService for that tariff are returned.
        Services already attached to the order are excluded from "available".
        Service matching rules:
        If the order's value for a Service FK (country_id, urgency_id, visa_duration_id, visa_type_id) is NULL, only services with the corresponding column IS NULL are allowed.
        Otherwise, services with the column IS NULL or equal to the order's value are allowed (i.e., global or matching services).
        Parameters:

        order_id (int): ID of the order to query.
        Returns:

        dict[str, Sequence | None]: {"attached": attached_services, "available": available_services}
        Raises:

        ValueError: if the order is not found or the client has no tariff_id.
        Notes:

        The method expects DB models with the following relations/columns: Order.client_id -> Client.id, Client.tariff_id OrderService.order_id, OrderService.service_id TariffService.service_id, TariffService.tariff_id
        Consider projecting only necessary columns or adding an index on (tariff_services.tariff_id, tariff_services.service_id) for large datasets.
        """
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
