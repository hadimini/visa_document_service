from urllib.parse import urljoin

from app.config import BACKEND_URL, JWT_EMAIL_CONFIRMATION_TOKEN_EXPIRES_DAYS
from app.models import Client, Order, User
from app.schemas.recipient import RecipientSchema, RecipientBodySchema
from app.services.jwt import JWTService

jwt_service = JWTService()


class RecipientService:
    def get_notified_by_email_confirm(self, *, user: User) -> RecipientSchema:
        token = jwt_service.create_email_confirmation_token(user=user)
        message = "Please confirm your email address by clicking the link below. This verification " \
                  "must be completed within the next {} days.".format(JWT_EMAIL_CONFIRMATION_TOKEN_EXPIRES_DAYS)
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

    async def get_notified_on_order_status_update(
            self,
            *,
            order: Order,
            old_status: str,
            new_status: str
    ) -> RecipientSchema:
        client = await order.awaitable_attrs.client
        subject = f"Order #{order.number} status updated"
        user_role: str = "manager" if client.type == Client.TYPE_LEGAL else "individual"
        old_status: str = dict(Order.STATUS_CHOICES).get(old_status)
        new_status: str = dict(Order.STATUS_CHOICES).get(new_status)
        message: str = f"Order #{order.number} status updated: from {old_status} to {new_status}"

        return RecipientSchema(
            email=client.email,
            subject=subject,
            body=RecipientBodySchema(
                title=subject,
                message=message,
                btn_url=urljoin(BACKEND_URL, f"{user_role}/orders/{order.id}"),
                btn_txt="Go to order"
            ),
        )
