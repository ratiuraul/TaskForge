from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.comments.models.comments_model import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_by_id(self, comment_id: int) -> Comment | None:
        query = select(Comment).where(Comment.id == comment_id)
        return self.db.scalar(query)

    def get_by_task_id(self, task_id: int) -> list[Comment]:
        query = select(Comment).where(Comment.task_id == task_id).order_by(Comment.id)
        return self.db.scalars(query).all()

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
        self.db.commit()

    def update(self, comment: Comment) -> Comment:
        self.db.commit()
        self.db.refresh(comment)
        return comment
