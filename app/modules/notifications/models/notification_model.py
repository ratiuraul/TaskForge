from sqlalchemy import func
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.common.enums import NotificationType
from datetime import datetime
from sqlalchemy import Enum as SQLEnum


class Notification(Base):

    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(
            NotificationType,
            values_callable=lambda enum: [e.value for e in enum],
            name="notificationtype",
        )
    )
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), nullable=True)
    read_at: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
