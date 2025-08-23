from app.models.users import User
from app.schemas.recipient import RecipientSchema
from app.services.jwt import JWTService

jwt_service = JWTService()


class RecipientService:
    def get_notified_by_email_confirm(self, *, user: User) -> RecipientSchema:
        confirmation_token = jwt_service.create_email_confirmation_token(user=user)
        return RecipientSchema(
            email=user.email,
            subject="Confirm your email",
            html=f"<h1>Confirm your email: {confirmation_token}</h1>"
        )
