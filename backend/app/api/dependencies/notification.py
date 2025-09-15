from app.services import NotificationService


async def get_notification_service() -> NotificationService:
    return NotificationService()
