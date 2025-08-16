from app.services.auth import AuthService
from app.services.email import EmailService
from app.services.jwt import JWTService
from app.services.notification import NotificationService
from app.services.recipient import RecipientService

auth_service = AuthService()
email_service = EmailService()
jwt_service = JWTService()
notification_service = NotificationService()
recipient_service = RecipientService()
