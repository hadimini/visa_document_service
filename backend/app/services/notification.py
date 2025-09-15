from app.models import Order, User

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

    async def notify_on_order_status_update(self, *, order: Order, old_status: str, new_status: str) -> None:
        recipient = await self.recipient_service.get_notified_on_order_status_update(
            order=order,
            old_status=old_status,
            new_status=new_status
        )
        await self.email_service.send([recipient])
