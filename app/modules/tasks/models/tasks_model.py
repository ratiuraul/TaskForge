from datetime import datetime

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import TaskPriority, TaskStatus
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(
            TaskPriority,
            values_callable=lambda enum: [e.value for e in enum],
            name="taskpriority",
        ),
        server_default=TaskPriority.LOW.value,
    )

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(
            TaskStatus,
            values_callable=lambda enum: [e.value for e in enum],
            name="taskstatus",
        ),
        server_default=TaskStatus.DRAFT.value,
    )
    story_points: Mapped[int | None]

    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    due_date: Mapped[datetime | None]
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
