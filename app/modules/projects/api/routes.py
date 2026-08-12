from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models.user_model import User
from app.modules.organizations.repository.organization_members_repository import (
    OrganizationMembersRepository,
)
from app.modules.projects.repository.projects_repository import ProjectRepository
from app.modules.projects.schemas.projects_schema import ProjectCreate, ProjectResponse
from app.modules.projects.services.projects_service import ProjectService

router = APIRouter(tags=["Projects"])


@router.post("/projects", response_model=ProjectResponse)
def create(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project_repository = ProjectRepository(db)
    organization_member_repository = OrganizationMembersRepository(db)

    project_service = ProjectService(
        project_repository=project_repository,
        org_member_repository=organization_member_repository,
    )

    return project_service.create(project, user)
