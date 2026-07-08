from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    username: str
