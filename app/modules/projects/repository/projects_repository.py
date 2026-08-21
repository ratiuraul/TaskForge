from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.projects.models import Project
from app.modules.organizations.models import OrganizationMember


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: int) -> Project | None:
        query = select(Project).where(Project.id == project_id)
        return self.db.scalar(query)

    def get_by_org_id(self, org_id: int) -> list[Project]:
        query = select(Project).where(Project.organization_id == org_id)
        return self.db.scalars(query).all()

    def get_by_name_and_org_id(self, name: str, org_id: int) -> Project | None:
        query = (
            select(Project)
            .where(Project.name == name)
            .where(Project.organization_id == org_id)
        )
        return self.db.scalar(query)

    def update(self, project: Project) -> Project:
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()

    def get_by_user_id(self, user_id: int) -> list[Project]:
        query = (
            select(Project)
            .join(
                OrganizationMember,
                Project.organization_id == OrganizationMember.organization_id,
            )
            .where(OrganizationMember.user_id == user_id)
        )

        result = self.db.scalars(query)
        return result.all()

    def get_by_id_and_user_id(self, project_id: int, user_id: int) -> Project:
        query = (
            select(Project)
            .join(
                OrganizationMember,
                Project.organization_id == OrganizationMember.organization_id,
            )
            .where(OrganizationMember.user_id == user_id)
            .where(Project.id == project_id)
        )

        result = self.db.scalar(query)
        return result
