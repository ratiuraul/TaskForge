from app.modules.comments.repository.comments_repository import CommentRepository
from app.modules.comments.schemas.comments_schema import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from app.modules.projects.repository.projects_repository import ProjectRepository
from app.modules.auth.models.user_model import User
from app.common.exceptions import InvalidTaskIdError, InvalidProjectIdError
from app.modules.comments.models.comments_model import Comment
from app.modules.tasks.repository.tasks_repository import TaskRepository


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        project_repo: ProjectRepository,
        task_repo: TaskRepository,
    ):
        self.comment_repo = comment_repo
        self.project_repo = project_repo
        self.task_repo = task_repo

    def create(
        self, task_id: int, comment: CommentCreate, current_user: User
    ) -> CommentResponse:
        task = self.task_repo.get_by_task_id(task_id=task_id)
        if not task:
            raise InvalidTaskIdError

        project_id = task.project_id
        available_project = self.project_repo.get_by_id_and_user_id(
            project_id=project_id, user_id=current_user.id
        )

        if not available_project:
            raise InvalidProjectIdError

        comment_model = Comment(
            task_id=task_id,
            author_id=current_user.id,
            body=comment.body,
        )

        created = self.comment_repo.create(comment_model)
        return CommentResponse.model_validate(created)
