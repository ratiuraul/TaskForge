from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.common.enums import TaskPriority, TaskStatus
from app.core.dependencies import get_db
from app.modules.tasks.schemas.tasks_schema import TaskResponse, TaskCreate, TaskUpdate
from app.modules.tasks.services.tasks_service import TaskService
from app.modules.tasks.repository.tasks_repository import TaskRepository
from app.modules.projects.repository.projects_repository import ProjectRepository

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models.user_model import User

router = APIRouter(tags=["Tasks"])


def get_task_service(db: Session) -> TaskService:
    task_repository = TaskRepository(db)
    project_repository = ProjectRepository(db)

    tasks_service = TaskService(
        task_repository=task_repository, project_repository=project_repository
    )

    return tasks_service


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
def create(
    project_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tasks_service = get_task_service(db=db)

    return tasks_service.create(task_create=task, project_id=project_id, user=user)


@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
def get_all(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    assigned_to_id: int = None,
    status: TaskStatus = None,
    priority: TaskPriority = None,
):
    tasks_service = get_task_service(db=db)

    return tasks_service.get_all_tasks(
        project_id=project_id,
        user=user,
        assigned_to_id=assigned_to_id,
        status=status,
        priority=priority,
    )


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def patch_task(
    patch_payload: TaskUpdate,
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tasks_service = get_task_service(db=db)

    patched_task = tasks_service.patch(
        patch_payload=patch_payload, task_id=task_id, user=user
    )

    return patched_task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    tasks_service = get_task_service(db=db)

    return tasks_service.get_by_id(task_id, user)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    tasks_service = get_task_service(db=db)

    tasks_service.delete(task_id, user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
