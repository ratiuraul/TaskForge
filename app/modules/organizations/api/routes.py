from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models.user_model import User
from app.modules.organizations.repository.organizations_repository import (
    OrganizationsRepository,
)
from app.modules.organizations.schemas.organizations_schema import (
    OrganizationCreate,
    OrganizationResponse,
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
    service = OrganizationsService(repository)
    created_org = service.create(organization, user)
    return created_org
