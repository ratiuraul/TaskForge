from app.common.exceptions import OrgAlreadyExistsError
from app.modules.auth.models.user_model import User
from app.modules.organizations.models.organizations_model import Organization
from app.modules.organizations.repository.organizations_repository import (
    OrganizationsRepository,
)
from app.modules.organizations.schemas.organizations_schema import (
    OrganizationCreate,
    OrganizationResponse,
)


class OrganizationsService:
    def __init__(self, repository: OrganizationsRepository):
        self.repository = repository

    def create(
        self, organization: OrganizationCreate, current_user: User
    ) -> OrganizationResponse:

        existing_org = self.repository.get_by_name(org_name=organization.name)
        if existing_org:
            raise OrgAlreadyExistsError

        organization_model = Organization(
            name=organization.name, owner_id=current_user.id
        )
        created_org = self.repository.create(organization_model)
        return OrganizationResponse.model_validate(created_org)
