from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models.user_model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> User:
        query = select(User).where(User.email == email)
        return self.db.scalar(query)

    def get_by_username(self, username: str) -> User:
        query = select(User).where(User.username == username)
        return self.db.scalar(query)

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)
