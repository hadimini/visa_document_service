from urllib.parse import urljoin

from app.config import BACKEND_URL, JWT_EMAIL_CONFIRMATION_TOKEN_EXPIRES_DAYS
from app.models.users import User
from app.schemas.recipient import RecipientSchema, RecipientBodySchema
from app.services.jwt import JWTService

jwt_service = JWTService()


class RecipientService:
    def get_notified_by_email_confirm(self, *, user: User) -> RecipientSchema:
        token = jwt_service.create_email_confirmation_token(user=user)
        message = f"Please confirm your email address by clicking the link below. This verification "\
                  "must be completed within the next {JWT_EMAIL_CONFIRMATION_TOKEN_EXPIRES_DAYS} days."
        return RecipientSchema(
            email=user.email,
            subject="Action Required: Verify Your Email",
            body=RecipientBodySchema(
                title="Action Required: Verify Your Email",
                message=message,
                btn_url=urljoin(BACKEND_URL, "auth/confirm-email?token=" + token),
                btn_txt="Confirm email address"
            )
        )
