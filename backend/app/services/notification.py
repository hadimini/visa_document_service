from app.models.users import User

from app.services.email import EmailService
from app.services.recipient import RecipientService


class NotificationService:
    def __init__(self):
        self.recipient_service = RecipientService()
        self.email_service = EmailService()

    async def notify_on_email_confirm(
            self,
            *,
            user: User,
    ) -> None:
        recipient = self.recipient_service.get_notified_by_email_confirm(user=user)
        await self.email_service.send([recipient])
