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
                template_body=recipient.body.model_dump(),
                subtype=MessageType.html,
            )
            await fm_mail.send_message(message, template_name="email_confirm.html")
