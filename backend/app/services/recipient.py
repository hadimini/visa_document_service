from app.models.users import User
from app.schemas.recipient import RecipientSchema


class RecipientService:
    def get_notified_by_email_confirm(self, *, user: User) -> RecipientSchema:
        return RecipientSchema(
            email=user.email,
            subject="Confirm your email",
            html="<h1>Confirm your email</h1>"
        )
