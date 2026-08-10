from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = UniqueConstraint(
        "name", "organization_id", name="uq_project_organization"
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
