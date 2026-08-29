from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.common.enums import OrganizationRole


class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    created_at: datetime


class OrganizationUpdate(BaseModel):
    name: str


class OrganizationMemberCreate(BaseModel):
    email: EmailStr
    role: OrganizationRole


class OrganizationMemberDelete(BaseModel):
    email: EmailStr


class OrganizationMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organization_id: int
    user_id: int
    role: OrganizationRole
    joined_at: datetime
