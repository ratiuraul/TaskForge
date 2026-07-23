from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.common.enums import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    username: str
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"