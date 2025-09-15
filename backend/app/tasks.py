from app.models import Order, User
from app.services import notification_service


async def task_notify_on_email_confirm(user: User):
    await notification_service.notify_on_email_confirm(user=user)


async def task_notify_on_order_status_update(order: Order, old_status: str, new_status: str):
    await notification_service.notify_on_order_status_update(order=order, old_status=old_status, new_status=new_status)
