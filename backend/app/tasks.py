from app.database.repositories.users import UsersRepository
from app.services import notification_service


async def task_notify_on_email_confirm(user_id: int, users_repo: UsersRepository):
    await notification_service.notify_on_email_confirm(user_id=user_id, users_repo=users_repo)
