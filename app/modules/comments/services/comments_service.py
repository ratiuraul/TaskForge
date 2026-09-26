from app.modules.comments.repository.comments_repository import CommentRepository
from app.modules.comments.schemas.comments_schema import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from app.modules.projects.repository.projects_repository import ProjectRepository
from app.modules.auth.models.user_model import User
from app.common.exceptions import (
    InvalidTaskIdError,
    InvalidProjectIdError,
    InvalidCommentIdError,
)
from app.modules.comments.models.comments_model import Comment
from app.modules.tasks.repository.tasks_repository import TaskRepository
from app.modules.notifications.models.notification_model import Notification
from app.modules.notifications.repository.notification_repository import (
    NotificationRepository,
)
from app.common.enums import NotificationType


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        project_repo: ProjectRepository,
        task_repo: TaskRepository,
        notification_repo: NotificationRepository,
    ):
        self.comment_repo = comment_repo
        self.project_repo = project_repo
        self.task_repo = task_repo
        self.notification_repo = notification_repo

    def _check_task_permissions(self, task_id: int, user_id: int):
        """
        Check if task exists and user is member of the organziation of the project where the task belongs to,
        Args:
            task_id (int): id of the task to be checked
            user_id (int): id of the current user

        Raises:
            InvalidTaskIdError: if task id is invalid
            InvalidProjectIdError: if user does not have access to that task
        """
        task = self.task_repo.get_by_task_id(task_id=task_id)
        if not task:
            raise InvalidTaskIdError

        project_id = task.project_id
        available_project = self.project_repo.get_by_id_and_user_id(
            project_id=project_id, user_id=user_id
        )

        if not available_project:
            raise InvalidProjectIdError

    def create(
        self, task_id: int, comment: CommentCreate, current_user: User
    ) -> CommentResponse:

        self._check_task_permissions(task_id=task_id, user_id=current_user.id)

        comment_model = Comment(
            task_id=task_id,
            author_id=current_user.id,
            body=comment.body,
        )

        created = self.comment_repo.create(comment_model)

        recipients_ids: set[int] = set()

        task = self.task_repo.get_by_task_id(task_id=task_id)

        if current_user.id != task.created_by_id:
            recipients_ids.add(task.created_by_id)

        if task.assigned_to_id and task.assigned_to_id != current_user.id:
            recipients_ids.add(task.assigned_to_id)

        for recipient_id in recipients_ids:
            notification_model = Notification(
                recipient_id=recipient_id,
                type=NotificationType.COMMENT_ON_TASK,
                task_id=task_id,
                comment_id=created.id,
            )

            self.notification_repo.create(notification=notification_model)

        return CommentResponse.model_validate(created)

    def patch(
        self, comment_id: int, comment: CommentUpdate, current_user: User
    ) -> CommentResponse:

        existing_comment = self.comment_repo.get_by_id(comment_id=comment_id)

        if not existing_comment:
            raise InvalidCommentIdError

        task_id = existing_comment.task_id

        self._check_task_permissions(task_id=task_id, user_id=current_user.id)

        existing_comment.body = comment.body
        self.comment_repo.update(existing_comment)

        comment_response = CommentResponse.model_validate(existing_comment)
        return comment_response

    def get_all(self, task_id: int, current_user: User) -> list[CommentResponse]:

        self._check_task_permissions(task_id=task_id, user_id=current_user.id)
        comments = self.comment_repo.get_by_task_id(task_id=task_id)
        return [CommentResponse.model_validate(comment) for comment in comments]

    def get_by_id(self, comment_id: int, current_user: User) -> CommentResponse:

        existing_comment = self.comment_repo.get_by_id(comment_id=comment_id)

        if not existing_comment:
            raise InvalidCommentIdError

        task_id = existing_comment.task_id

        self._check_task_permissions(task_id=task_id, user_id=current_user.id)

        return CommentResponse.model_validate(existing_comment)

    def delete(self, comment_id: int, current_user: User) -> None:

        existing_comment = self.comment_repo.get_by_id(comment_id=comment_id)

        if not existing_comment:
            raise InvalidCommentIdError

        task_id = existing_comment.task_id

        self._check_task_permissions(task_id=task_id, user_id=current_user.id)

        self.comment_repo.delete(comment=existing_comment)
