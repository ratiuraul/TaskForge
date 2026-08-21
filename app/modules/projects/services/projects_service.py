from app.common.exceptions import (
    InvalidProjectIdError,
    NotOrgMember,
    ProjectAlreadyExists,
)
from app.modules.auth.models.user_model import User
from app.modules.organizations.repository.organization_members_repository import (
    OrganizationMembersRepository,
)
from app.modules.projects.models import Project
from app.modules.projects.repository.projects_repository import ProjectRepository
from app.modules.projects.schemas.projects_schema import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)


class ProjectService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        org_member_repository: OrganizationMembersRepository,
    ):
        self.project_repository = project_repository
        self.org_member_repository = org_member_repository

    def create(self, project: ProjectCreate, current_user: User) -> ProjectResponse:

        is_org_member = self.org_member_repository.get_membership(
            project.organization_id, current_user.id
        )

        if not is_org_member:
            raise NotOrgMember

        project_already_exists = self.project_repository.get_by_name_and_org_id(
            name=project.name, org_id=project.organization_id
        )

        if project_already_exists:
            raise ProjectAlreadyExists

        project_model = Project(
            name=project.name,
            description=project.description,
            organization_id=project.organization_id,
        )

        created_project = self.project_repository.create(project_model)
        return ProjectResponse.model_validate(created_project)

    def get_by_id(self, project_id: int, current_user: User) -> ProjectResponse | None:

        project = self.project_repository.get_by_id(project_id)

        if not project:
            raise InvalidProjectIdError

        is_org_member = self.org_member_repository.get_membership(
            project.organization_id, current_user.id
        )

        if not is_org_member:
            raise NotOrgMember

        return ProjectResponse.model_validate(project)

    def get_all(self, current_user: User) -> list[ProjectResponse] | None:
        projects = self.project_repository.get_by_user_id(current_user.id)
        return [ProjectResponse.model_validate(project) for project in projects]

    def patch(
        self, patch_payload: ProjectUpdate, project_id: int, user: User
    ) -> ProjectResponse | None:

        existing_project = self.project_repository.get_by_id_and_user_id(
            project_id=project_id, user_id=user.id
        )

        if not existing_project:
            raise InvalidProjectIdError

        project_name = (
            patch_payload.name if patch_payload.name else existing_project.name
        )
        org_id = (
            patch_payload.organization_id
            if patch_payload.organization_id
            else existing_project.organization_id
        )

        project_already_exists = self.project_repository.get_by_name_and_org_id(
            name=project_name, org_id=org_id
        )

        if project_already_exists:
            raise ProjectAlreadyExists

        is_org_member = self.org_member_repository.get_membership(org_id, user.id)

        if not is_org_member:
            raise NotOrgMember

        existing_project.name = project_name
        existing_project.organization_id = org_id
        existing_project.description = patch_payload.description

        updated = self.project_repository.update(existing_project)

        return ProjectResponse.model_validate(updated)
