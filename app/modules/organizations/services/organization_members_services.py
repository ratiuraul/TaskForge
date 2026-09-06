from app.common.enums import OrganizationRole
from app.common.exceptions import (
    InsufficientPrivilegesError,
    InvalidOrgIdError,
    InvalidUserId,
    NotOrgMember,
    UserIsAlreadyMember,
)
from app.modules.auth.models.user_model import User
from app.modules.auth.repository.user_repository import UserRepository
from app.modules.auth.schemas.user_schema import UserResponse
from app.modules.organizations.models.organizations_model import (
    OrganizationMember,
)
from app.modules.organizations.repository.organization_members_repository import (
    OrganizationMembersRepository,
)
from app.modules.organizations.repository.organizations_repository import (
    OrganizationsRepository,
)
from app.modules.organizations.schemas.organizations_schema import (
    OrganizationMemberCreate,
    OrganizationMemberDelete,
    OrganizationMemberResponse,
)


class OrganizationsMembersService:
    def __init__(
        self,
        repository: OrganizationsRepository,
        member_repository: OrganizationMembersRepository,
        user_repository: UserRepository,
    ):
        self.repository = repository
        self.member_repository = member_repository
        self.user_repository = user_repository

    def check_opperation_allowed(
        self,
        current_user: User,
        org_id: int,
        organization_member: OrganizationMemberCreate
        | OrganizationMemberDelete
        | None = None,
        organization_roles: list[OrganizationRole] | None = None,
    ):
        """
        checks:
            organization exists
            target user exists
            current user is member of organization
            current user is owner or admin of organziation
        """

        organization = self.repository.get_by_id(org_id=org_id, user_id=current_user.id)
        if not organization:
            raise InvalidOrgIdError

        if organization_member:
            user = self.user_repository.get_by_email(email=organization_member.email)

            if not user:
                raise InvalidUserId

        if not organization_roles:
            organization_roles = [
                OrganizationRole.OWNER,
                OrganizationRole.ADMIN,
            ]

        current_user_membership = self.member_repository.get_membership(
            org_id, current_user.id
        )

        if not current_user_membership:
            raise NotOrgMember

        if not current_user_membership.role in organization_roles:
            raise InsufficientPrivilegesError

    def create(
        self,
        organization_member: OrganizationMemberCreate,
        current_user: User,
        org_id: int,
    ) -> OrganizationMemberResponse:

        self.check_opperation_allowed(
            current_user,
            org_id,
            organization_member,
        )

        user = self.user_repository.get_by_email(email=organization_member.email)

        is_already_member = self.member_repository.get_membership(org_id, user.id)

        if is_already_member:
            raise UserIsAlreadyMember

        current_user_role = self.member_repository.get_org_role(org_id, current_user.id)

        if (
            organization_member.role == OrganizationRole.OWNER
            and current_user_role != OrganizationRole.OWNER
        ):
            raise InsufficientPrivilegesError

        organization_member = OrganizationMember(
            organization_id=org_id,
            user_id=user.id,
            role=organization_member.role,
        )

        created_member = self.member_repository.create(organization_member)

        return OrganizationMemberResponse.model_validate(created_member)

    def delete(
        self,
        organization_member: OrganizationMemberDelete,
        current_user: User,
        org_id: int,
    ) -> None:

        self.check_opperation_allowed(
            current_user,
            org_id,
            organization_member,
        )
        target_user = self.user_repository.get_by_email(organization_member.email)
        is_target_user_member = self.member_repository.get_membership(
            org_id, target_user.id
        )
        if not is_target_user_member:
            raise NotOrgMember

        current_user_role = self.member_repository.get_org_role(org_id, current_user.id)

        if (
            target_user.role == OrganizationRole.OWNER
            and current_user_role != OrganizationRole.OWNER
        ):
            raise InsufficientPrivilegesError
        self.member_repository.delete_by_user_and_org_id(org_id, target_user.id)

    def get_members(self, current_user: User, org_id: int) -> list[UserResponse]:
        self.check_opperation_allowed(
            current_user,
            org_id,
            organization_roles=[
                OrganizationRole.OWNER,
                OrganizationRole.ADMIN,
                OrganizationRole.MEMBER,
            ],
        )
        members = self.user_repository.get_by_org_id(org_id)
        return [UserResponse.model_validate(member) for member in members]
