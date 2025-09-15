from fastapi import Depends

from app.api.dependencies.db import get_repository
from app.api.dependencies.notification import get_notification_service
from app.database.repositories.audit import AuditRepository
from app.database.repositories.orders import OrdersRepository
from app.services import NotificationService
from app.services.order import OrderService


async def get_order_service(
        orders_repo: OrdersRepository = Depends(get_repository(OrdersRepository)),
        audit_repo: AuditRepository = Depends(get_repository(AuditRepository)),
        notification_service: NotificationService = Depends(get_notification_service)
) -> OrderService:
    return OrderService(orders_repo, audit_repo, notification_service)
