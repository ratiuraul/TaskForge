from sqlalchemy.orm import Session
from app.modules.tasks.models import Task
from sqlalchemy import select
from app.common.enums import TaskPriority, TaskStatus


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def get_by_task_id(self, task_id: int) -> Task | None:
        query = select(Task).where(Task.id == task_id)
        return self.db.scalar(query)

    def get_all_project_id(
        self,
        project_id: int,
        assigned_to_id: int = None,
        status: TaskStatus = None,
        priority: TaskPriority = None,
    ) -> list[Task]:
        query = select(Task).where(Task.project_id == project_id)

        if assigned_to_id is not None:
            query = query.where(Task.assigned_to_id == assigned_to_id)

        if status is not None:
            query = query.where(Task.status == status)

        if priority is not None:
            query = query.where(Task.priority == priority)

        return self.db.scalars(query).all()
