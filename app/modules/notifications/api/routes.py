from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models.user_model import User
from app.modules.notifications.repository.notification_repository import (
    NotificationRepository,
)
from app.modules.notifications.schemas.notification_schema import NotificationResponse
from app.modules.notifications.services.notification_service import NotificationService

router = APIRouter(tags=["Notifications"])


def get_notification_service(db: Session) -> NotificationService:
    return NotificationService(notification_repo=NotificationRepository(db))


@router.get("/notifications", response_model=list[NotificationResponse])
def get_all(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_notification_service(db).get_all(current_user=user)


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_notification_service(db).mark_read(
        notification_id=notification_id, current_user=user
    )
