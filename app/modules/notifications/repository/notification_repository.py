from sqlalchemy.orm import Session
from app.modules.notifications.models.notification_model import Notification
from sqlalchemy import select


class NotificationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def update(self, notification: Notification) -> Notification:
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_by_id(self, notification_id: int) -> Notification | None:
        query = select(Notification).where(Notification.id == notification_id)
        return self.db.scalar(query)

    def get_by_recipient_id(self, user_id: int) -> list[Notification]:
        query = (
            select(Notification)
            .where(Notification.recipient_id == user_id)
            .order_by(Notification.id.desc())
        )
        return self.db.scalars(query).all()
