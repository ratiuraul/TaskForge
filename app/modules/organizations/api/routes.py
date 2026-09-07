from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models.user_model import User
from app.modules.auth.repository.user_repository import UserRepository
from app.modules.auth.schemas.user_schema import UserResponse
from app.modules.organizations.repository.organization_members_repository import (
    OrganizationMembersRepository,
)
from app.modules.organizations.repository.organizations_repository import (
    OrganizationsRepository,
)
from app.modules.organizations.schemas.organizations_schema import (
    OrganizationCreate,
    OrganizationMemberCreate,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.modules.organizations.services.organization_members_services import (
    OrganizationsMembersService,
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


@router.post(
    "/organizations/{org_id}/members", response_model=OrganizationMemberResponse
)
def add_org_member(
    org_id: int,
    org_member: OrganizationMemberCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = OrganizationsRepository(db)
    member_repository = OrganizationMembersRepository(db)
    user_repository = UserRepository(db)
    service = OrganizationsMembersService(
        repository, member_repository, user_repository=user_repository
    )
    added_member = service.create(
        organization_member=org_member, current_user=user, org_id=org_id
    )
    return added_member


@router.delete(
    "/organizations/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_org_member(
    org_id: int,
    user_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = OrganizationsRepository(db)
    member_repository = OrganizationMembersRepository(db)
    user_repository = UserRepository(db)
    service = OrganizationsMembersService(
        repository, member_repository, user_repository=user_repository
    )
    service.delete(user_id, user, org_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/organizations/{org_id}/members", response_model=list[UserResponse])
def get_users_for_org(
    org_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    repository = OrganizationsRepository(db)
    member_repository = OrganizationMembersRepository(db)
    user_repository = UserRepository(db)
    service = OrganizationsMembersService(
        repository, member_repository, user_repository=user_repository
    )
    return service.get_members(user, org_id)
