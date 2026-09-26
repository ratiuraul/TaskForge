from fastapi import APIRouter, Depends, Response, status
from app.modules.comments.schemas.comments_schema import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from sqlalchemy.orm import Session

from app.modules.auth.models.user_model import User
from app.core.dependencies import get_db
from app.modules.auth.dependencies import get_current_user

from app.modules.comments.services.comments_service import CommentService
from app.modules.tasks.repository.tasks_repository import TaskRepository
from app.modules.projects.repository.projects_repository import ProjectRepository
from app.modules.comments.repository.comments_repository import CommentRepository
from app.modules.notifications.repository.notification_repository import (
    NotificationRepository,
)

router = APIRouter(tags=["Comments"])


def get_comment_service(db: Session) -> CommentService:
    project_repo = ProjectRepository(db=db)
    task_repo = TaskRepository(db=db)
    comment_repo = CommentRepository(db=db)
    notification_repo = NotificationRepository(db=db)

    comment_service = CommentService(
        comment_repo=comment_repo,
        project_repo=project_repo,
        task_repo=task_repo,
        notification_repo=notification_repo,
    )

    return comment_service


@router.post("/tasks/{task_id}/comments", response_model=CommentResponse)
def create(
    task_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    comments_service = get_comment_service(db=db)

    return comments_service.create(task_id=task_id, comment=comment, current_user=user)


@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse])
def get_all_comments(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    comments_service = get_comment_service(db=db)
    return comments_service.get_all(task_id=task_id, current_user=user)


@router.get("/comments/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    comments_service = get_comment_service(db=db)
    return comments_service.get_by_id(comment_id=comment_id, current_user=user)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
def patch_comment(
    comment_id: int,
    comment_patch: CommentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    comments_service = get_comment_service(db=db)
    return comments_service.patch(
        comment_id=comment_id, comment=comment_patch, current_user=user
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    comments_service = get_comment_service(db=db)
    comments_service.delete(comment_id=comment_id, current_user=user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
