from fastapi import BackgroundTasks

from app.database.repositories.audit import AuditRepository
from app.database.repositories.orders import OrdersRepository
from app.exceptions import NotFoundException
from app.models import Order, LogEntry
from app.schemas.audit import LogEntryCreateSchema
from app.schemas.order.admin import AdminOrderCreateSchema, AdminOrderUpdateSchema
from app.services.notification import NotificationService
from app.tasks import task_notify_on_order_status_update


class OrderService:
    """Service class for managing orders, including creation and updates.

        This class provides methods to create and update orders, as well as to log
        actions and send notifications when order statuses change.

        Attributes:
            orders_repo (OrdersRepository): Repository for accessing order data.
            audit_repo (AuditRepository): Repository for logging actions.
            notification_service (NotificationService): Service for handling notifications.
        """

    def __init__(
            self,
            orders_repo: OrdersRepository,
            audit_repo: AuditRepository,
            notification_service: NotificationService,
    ):
        """Initialize the OrderService with the necessary repositories and services.

        Args:
            orders_repo (OrdersRepository): The repository for accessing order data.
            audit_repo (AuditRepository): The repository for logging actions.
            notification_service (NotificationService): The service for handling notifications.
        """
        self.orders_repo = orders_repo
        self.audit_repo = audit_repo
        self.notification_service = notification_service

    async def create_order(self, data: AdminOrderCreateSchema) -> Order:
        """Create a new order in the system.

        This method adds a new order based on the provided data schema and
        commits it to the database.

        Args:
            data (AdminOrderCreateSchema): The data schema containing order details.

        Returns:
            Order: The created order instance.
        """
        ...

    async def update_order(
            self,
            *,
            order_id: int,
            data: AdminOrderUpdateSchema,
            user_id: int,
            bg_tasks: BackgroundTasks,
            populate_client: bool = False,

    ) -> Order:
        """Update an existing order in the system.

        This method modifies an existing order based on the provided data schema
        and logs the action. It also sends a notification if the order status changes.

        Args:
            order_id (int): The ID of the order to update.
            data (AdminOrderUpdateSchema): The data schema containing updated order details.
            user_id (int): The ID of the user making the update.
            bg_tasks (BackgroundTasks): Background tasks to be executed after the response is sent.
            populate_client (bool): Whether to include client data in the returned order. Defaults to False.

        Returns:
            Order: The updated order instance.

        Raises:
            NotFoundException: If the order with the specified ID does not exist.
        """
        current_order = await self.orders_repo.get_by_id(order_id=order_id)

        if not current_order:
            raise NotFoundException(detail="Order not found")

        old_status = current_order.status

        updated_order = await self.orders_repo.update(
            order_id=order_id,
            data=data,
            populate_client=populate_client
        )

        await self.audit_repo.create(
            data=LogEntryCreateSchema(
                user_id=user_id,
                action=LogEntry.ACTION_UPDATE,
                model_type=Order.get_model_type(),
                target_id=updated_order.id
            )
        )

        if old_status != updated_order.status:
            bg_tasks.add_task(task_notify_on_order_status_update, updated_order, old_status, updated_order.status)

        return updated_order
