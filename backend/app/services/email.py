from fastapi_mail import FastMail, MessageSchema, MessageType

from app.config import mail_config
from app.schemas.recipient import RecipientSchema


class EmailService:
    fm: FastMail = FastMail(mail_config)

    @staticmethod
    async def send(recipients: list[RecipientSchema]):
        for recipient in recipients:
            message = MessageSchema(
                subject=recipient.subject,
                recipients=[recipient.email],
                body=recipient.html,
                subtype=MessageType.html,
            )

            await EmailService.fm.send_message(message)
