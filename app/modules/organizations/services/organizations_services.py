from app.common.enums import OrganizationRole
from app.common.exceptions import InvalidOrgIdError, OrgAlreadyExistsError
from app.modules.auth.models.user_model import User
from app.modules.organizations.models.organizations_model import (
    Organization,
    OrganizationMember,
)
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


class OrganizationsService:
    def __init__(
        self,
        repository: OrganizationsRepository,
        member_repository: OrganizationMembersRepository,
    ):
        self.repository = repository
        self.member_repository = member_repository

    def create(
        self, organization: OrganizationCreate, current_user: User
    ) -> OrganizationResponse:

        existing_org = self.repository.get_by_name(org_name=organization.name)
        if existing_org:
            raise OrgAlreadyExistsError

        organization_model = Organization(name=organization.name)
        created_org = self.repository.create(organization_model)

        organization_member = OrganizationMember(
            organization_id=created_org.id,
            user_id=current_user.id,
            role=OrganizationRole.OWNER,
        )

        self.member_repository.create(organization_member)

        return OrganizationResponse.model_validate(created_org)

    def get(self, org_id: int, user: User) -> OrganizationResponse | None:
        org_details = self.repository.get_by_id(org_id, user.id)
        if not org_details:
            raise InvalidOrgIdError

        return OrganizationResponse.model_validate(org_details)

    def get_all(self, user: User) -> list[OrganizationResponse]:
        organizations = self.repository.get_all_by_user(user.id)
        return [OrganizationResponse.model_validate(org) for org in organizations]

    def patch(
        self, patch_payload: OrganizationUpdate, org_id: int, user: int
    ) -> OrganizationResponse | None:
        organization = self.repository.get_by_id(org_id=org_id, user_id=user.id)
        if not organization:
            raise InvalidOrgIdError

        existing = self.repository.get_by_name(patch_payload.name)
        if existing and existing.id != organization.id:
            raise OrgAlreadyExistsError

        organization.name = patch_payload.name

        updated = self.repository.update(organization)

        return OrganizationResponse.model_validate(updated)

    def delete(self, org_id: int, user: User) -> None:
        organization = self.repository.get_by_id(org_id=org_id, user_id=user.id)
        if not organization:
            raise InvalidOrgIdError

        self.member_repository.delete_by_organization(org_id)
        self.repository.delete(organization)
