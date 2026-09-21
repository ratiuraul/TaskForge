from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CommentCreate(BaseModel):
    body: str


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    task_id: int
    author_id: int
    body: str
    created_at: datetime


class CommentUpdate(BaseModel):
    body: str
