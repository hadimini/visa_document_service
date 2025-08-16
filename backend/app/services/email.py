from app.schemas.recipient import RecipientSchema


def write_notification(email: str, message=""):
    with open("log.txt", mode="a") as email_file:
        content = f"\nnotification for {email}: {message}"
        email_file.write(content)


class EmailService:
    @staticmethod
    def send(recipients: list[RecipientSchema]):
        for recipient in recipients:
            write_notification(recipient.email, message=recipient.subject)
