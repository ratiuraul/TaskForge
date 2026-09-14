from pydantic import BaseModel, ConfigDict, Field
from app.common.enums import TaskPriority, TaskStatus
from datetime import datetime


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    story_points: int | None = None
    assigned_to_id: int | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_id: int
    project_id: int

    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    story_points: int | None
    assigned_to_id: int | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    project_id: int | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    story_points: int | None = None
    assigned_to_id: int | None = None
    due_date: datetime | None = None
