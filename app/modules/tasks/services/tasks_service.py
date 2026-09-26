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
from app.common.enums import NotificationType, TaskPriority, TaskStatus
from app.modules.notifications.services.notification_service import NotificationService


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository,
        project_repository: ProjectRepository,
        notification_service: NotificationService,
    ) -> None:
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.notification_service = notification_service

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
        users_projects = self.project_repository.get_by_id_and_user_id(
            project_id=project_id, user_id=user.id
        )

        if not users_projects:
            raise InvalidProjectIdError

        if task_create.assigned_to_id is not None:
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

        if created_task.assigned_to_id and created_task.assigned_to_id != user.id:
            self.notification_service.create(
                recipient_id=created_task.assigned_to_id,
                notification_type=NotificationType.TASK_ASSIGNED,
                task_id=created_task.id,
            )

        return TaskResponse.model_validate(created_task)

    def patch(
        self, patch_payload: TaskUpdate, task_id: int, user: User
    ) -> TaskResponse:
        existing_task = self.get_task_for_user(task_id=task_id, user=user)

        updates = patch_payload.model_dump(exclude_unset=True)
        previous_assignee_id = existing_task.assigned_to_id

        if "project_id" in updates:
            new_project_id = updates["project_id"]
            is_valid_project_id = self.project_repository.get_by_id_and_user_id(
                project_id=new_project_id, user_id=user.id
            )
            if not is_valid_project_id:
                raise InvalidProjectIdError

            assignee_id = updates.get("assigned_to_id", existing_task.assigned_to_id)
            if assignee_id is not None:
                assignee_can_access_target = (
                    self.project_repository.get_by_id_and_user_id(
                        project_id=new_project_id, user_id=assignee_id
                    )
                )
                if not assignee_can_access_target:
                    raise InvalidAsigneeIdError

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

        if (
            "assigned_to_id" in updates
            and updated.assigned_to_id is not None
            and updated.assigned_to_id != previous_assignee_id
            and updated.assigned_to_id != user.id
        ):
            self.notification_service.create(
                recipient_id=updated.assigned_to_id,
                notification_type=NotificationType.TASK_ASSIGNED,
                task_id=updated.id,
            )

        return TaskResponse.model_validate(updated)

    def get_all_tasks(
        self,
        project_id: int,
        user: User,
        assigned_to_id: int = None,
        status: TaskStatus = None,
        priority: TaskPriority = None,
        limit=20,
        offset=0,
    ) -> list[TaskResponse]:
        users_projects = self.project_repository.get_by_id_and_user_id(
            project_id=project_id, user_id=user.id
        )

        if not users_projects:
            raise InvalidProjectIdError

        tasks = self.task_repository.get_all_project_id(
            project_id=project_id,
            assigned_to_id=assigned_to_id,
            status=status,
            priority=priority,
            limit=limit,
            offset=offset,
        )

        return [TaskResponse.model_validate(task) for task in tasks]

    def get_by_id(self, task_id: int, user: User) -> TaskResponse:
        task = self.get_task_for_user(task_id=task_id, user=user)
        return TaskResponse.model_validate(task)

    def delete(self, task_id: int, user: User) -> None:
        task = self.get_task_for_user(task_id=task_id, user=user)
        self.task_repository.delete(task)
