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
from app.modules.projects.schemas.projects_schema import ProjectCreate, ProjectResponse


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
