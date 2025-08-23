from app.models.users import User
from app.services import notification_service


async def task_notify_on_email_confirm(user: User):
    await notification_service.notify_on_email_confirm(user=user)
