from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import UserRole
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
    )
