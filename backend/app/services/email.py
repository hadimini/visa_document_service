import logging
import requests

from app.config import MAILGUN_API_KEY, MAILGUN_API_URL
from app.schemas.recipient import RecipientSchema


def write_notification(email: str, message=""):
    with open("log.txt", mode="a") as email_file:
        content = f"\nnotification for {email}: {message}"
        email_file.write(content)


class EmailService:
    @staticmethod
    def send(recipients: list[RecipientSchema]):
        for recipient in recipients:
            try:
                response = requests.post(
                    MAILGUN_API_URL,
                    auth=("api", MAILGUN_API_KEY),
                    data={
                        "from": "hadimini@gmail.com",
                        "to": recipient.email,
                        "subject": recipient.subject,
                        "html": recipient.html,
                    }
                )
                if response.status_code != 200:
                    logging.error(f"failed to send email to {recipient.email}")
                else:
                    logging.info(f"Successfully sent an email to '{recipient.email}' via Mailgun API.")
            except Exception as e:
                logging.exception(f"Mailgun error: {e}")
