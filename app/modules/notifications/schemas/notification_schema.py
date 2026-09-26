from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.common.enums import NotificationType


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_id: int
    type: NotificationType
    task_id: int
    comment_id: int | None
    read_at: datetime | None
    created_at: datetime
