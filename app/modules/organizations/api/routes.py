from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models.user_model import User
from app.modules.organizations.repository.organization_members_repository import (
    OrganizationMembersRepository,
)
from app.modules.organizations.repository.organizations_repository import (
    OrganizationsRepository,
)
from app.modules.organizations.schemas.organizations_schema import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.modules.organizations.services.organizations_services import (
    OrganizationsService,
)

router = APIRouter(tags=["Organizations"])


@router.post("/organizations", response_model=OrganizationResponse)
def create(
    organization: OrganizationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = OrganizationsRepository(db)
    member_repository = OrganizationMembersRepository(db)
    service = OrganizationsService(repository, member_repository)
    created_org = service.create(organization, user)
    return created_org


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
def get(
    org_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    repository = OrganizationsRepository(db)
    member_repository = OrganizationMembersRepository(db)
    service = OrganizationsService(repository, member_repository)
    org_details = service.get(org_id, user)
    return org_details


@router.get("/organizations", response_model=list[OrganizationResponse])
def get_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repository = OrganizationsRepository(db)
    member_repository = OrganizationMembersRepository(db)
    service = OrganizationsService(repository, member_repository)
    organizations = service.get_all(user)
    return organizations


@router.patch("/organizations/{org_id}", response_model=OrganizationResponse)
def patch_org(
    patch_payload: OrganizationUpdate,
    org_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = OrganizationsRepository(db)
    member_repository = OrganizationMembersRepository(db)
    service = OrganizationsService(repository, member_repository)
    patched_org = service.patch(patch_payload, org_id, user)
    return patched_org


@router.delete(
    "/organizations/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_org(
    org_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = OrganizationsRepository(db)
    member_repository = OrganizationMembersRepository(db)
    service = OrganizationsService(repository, member_repository)
    service.delete(org_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
