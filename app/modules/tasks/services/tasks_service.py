from app.modules.tasks.repository.tasks_repository import TaskRepository
from app.modules.tasks.schemas.tasks_schema import TaskCreate, TaskUpdate, TaskResponse
from app.modules.auth.models.user_model import User
from app.modules.projects.repository.projects_repository import ProjectRepository
from app.common.exceptions import (
    InvalidProjectIdError,
    InvalidTaskIdError,
    InvalidAsigneeIdError,
)
from app.modules.tasks.models.tasks_model import Task
from app.common.enums import TaskPriority, TaskStatus


class TaskService:
    def __init__(
        self, task_repository: TaskRepository, project_repository: ProjectRepository
    ) -> None:
        self.task_repository = task_repository
        self.project_repository = project_repository

    def get_task_for_user(self, task_id: int, user: User) -> Task:
        task = self.task_repository.get_by_task_id(task_id)

        if not task:
            raise InvalidTaskIdError

        project_id = task.project_id

        users_projects = self.project_repository.get_by_id_and_user_id(
            project_id=project_id, user_id=user.id
        )

        if not users_projects:
            raise InvalidProjectIdError

        return task

    def create(
        self, task_create: TaskCreate, project_id: int, user: User
    ) -> TaskResponse:
        # user has access to project?

        users_projects = self.project_repository.get_by_id_and_user_id(
            project_id=project_id, user_id=user.id
        )

        if not users_projects:
            raise InvalidProjectIdError

        if task_create.assigned_to_id is not None:
            # is assigned user member of projects org?
            assign_users_projects = self.project_repository.get_by_id_and_user_id(
                project_id=project_id, user_id=task_create.assigned_to_id
            )
            if not assign_users_projects:
                raise InvalidAsigneeIdError

        task_model = Task(
            title=task_create.title,
            description=task_create.description,
            priority=task_create.priority or TaskPriority.LOW,
            status=task_create.status or TaskStatus.DRAFT,
            story_points=task_create.story_points,
            assigned_to_id=task_create.assigned_to_id,
            due_date=task_create.due_date,
            created_by_id=user.id,
            project_id=project_id,
        )

        created_task = self.task_repository.create(task_model)

        return TaskResponse.model_validate(created_task)

    def patch(
        self, patch_payload: TaskUpdate, task_id: int, user: User
    ) -> TaskResponse:
        # Valid task id?
        existing_task = self.get_task_for_user(task_id=task_id, user=user)

        # Get only the user sent key/values

        updates = patch_payload.model_dump(exclude_unset=True)

        if "project_id" in updates:
            new_project_id = updates["project_id"]
            is_valid_project_id = self.project_repository.get_by_id_and_user_id(
                project_id=new_project_id, user_id=user.id
            )
            if not is_valid_project_id:
                raise InvalidProjectIdError

        if "assigned_to_id" in updates:
            assignee_id = updates["assigned_to_id"]
            if assignee_id is not None:
                target_project_id = updates.get("project_id", existing_task.project_id)
                is_valid_project_id = self.project_repository.get_by_id_and_user_id(
                    project_id=target_project_id, user_id=assignee_id
                )
                if not is_valid_project_id:
                    raise InvalidAsigneeIdError

        for field_name, value in updates.items():
            setattr(existing_task, field_name, value)

        updated = self.task_repository.update(existing_task)
        return TaskResponse.model_validate(updated)

    def get_all_tasks(self, project_id: int, user: User) -> list[TaskResponse]:
        users_projects = self.project_repository.get_by_id_and_user_id(
            project_id=project_id, user_id=user.id
        )

        if not users_projects:
            raise InvalidProjectIdError

        tasks = self.task_repository.get_all_project_id(project_id=project_id)

        return [TaskResponse.model_validate(task) for task in tasks]

    def get_by_id(self, task_id: int, user: User) -> TaskResponse:

        task = self.get_task_for_user(task_id=task_id, user=user)

        return TaskResponse.model_validate(task)

    def delete(self, task_id: int, user: User) -> None:

        task = self.get_task_for_user(task_id=task_id, user=user)

        self.task_repository.delete(task)
