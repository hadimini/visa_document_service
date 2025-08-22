from app.database.repositories.users import UsersRepository
from app.services.email import EmailService
from app.services.recipient import RecipientService


class NotificationService:
    def __init__(self):
        self.recipient_service = RecipientService()
        self.email_service = EmailService()

    async def notify_on_email_confirm(
            self,
            *,
            user_id: int,
            users_repo: UsersRepository
    ) -> None:
        user = await users_repo.get_by_id(user_id=user_id)
        recipient = self.recipient_service.get_notified_by_email_confirm(user=user)
        # self.email_service.send([recipient])
