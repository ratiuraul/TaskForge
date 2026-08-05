from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.organizations.models import Organization, OrganizationMember


class OrganizationsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, organization: Organization) -> Organization:
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def get_all_by_user(self, user_id: int) -> list[Organization]:
        query = (
            select(Organization)
            .join(
                OrganizationMember,
                Organization.id == OrganizationMember.organization_id,
            )
            .where(OrganizationMember.user_id == user_id)
        )

        result = self.db.scalars(query)
        return result.all()

    def get_by_id(self, org_id: int, user_id: int) -> Organization | None:

        query = (
            select(Organization)
            .join(
                OrganizationMember,
                Organization.id == OrganizationMember.organization_id,
            )
            .where(Organization.id == org_id)
            .where(OrganizationMember.user_id == user_id)
        )

        return self.db.scalar(query)

    def get_by_name(self, org_name: str) -> Organization | None:
        query = select(Organization).where(Organization.name == org_name)
        return self.db.scalar(query)

    def update(self, organization: Organization) -> Organization:
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def delete(self, organization: Organization) -> None:
        self.db.delete(organization)
        self.db.commit()
