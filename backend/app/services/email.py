from fastapi_mail import MessageSchema, MessageType

from app.config import fm_mail
from app.schemas.recipient import RecipientSchema


class EmailService:

    @staticmethod
    async def send(recipients: list[RecipientSchema]):
        for recipient in recipients:
            message = MessageSchema(
                subject=recipient.subject,
                recipients=[recipient.email],
                body=recipient.html,
                subtype=MessageType.html,
            )
            await fm_mail.send_message(message)
