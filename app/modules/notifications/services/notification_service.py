from datetime import datetime

from app.common.enums import NotificationType
from app.common.exceptions import InvalidNotificationIdError
from app.modules.auth.models.user_model import User
from app.modules.notifications.models.notification_model import Notification
from app.modules.notifications.repository.notification_repository import (
    NotificationRepository,
)
from app.modules.notifications.schemas.notification_schema import NotificationResponse


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    def create(
        self,
        recipient_id: int,
        notification_type: NotificationType,
        task_id: int,
        comment_id: int | None = None,
    ) -> Notification:
        notification = Notification(
            recipient_id=recipient_id,
            type=notification_type,
            task_id=task_id,
            comment_id=comment_id,
        )
        return self.notification_repo.create(notification)

    def get_all(self, current_user: User) -> list[NotificationResponse]:
        notifications = self.notification_repo.get_by_recipient_id(
            user_id=current_user.id
        )
        return [
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ]

    def mark_read(
        self, notification_id: int, current_user: User
    ) -> NotificationResponse:
        notification = self.notification_repo.get_by_id(notification_id)

        if not notification or notification.recipient_id != current_user.id:
            raise InvalidNotificationIdError

        notification.read_at = datetime.now()
        updated = self.notification_repo.update(notification)
        return NotificationResponse.model_validate(updated)
