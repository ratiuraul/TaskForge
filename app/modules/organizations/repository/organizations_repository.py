from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.organizations.models import Organization


class OrganizationsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, organization: Organization) -> Organization:
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def get_all_by_owner(self, owner_id: int) -> list[Organization]:
        query = select(Organization).where(Organization.owner_id == owner_id)
        result = self.db.scalars(query)
        return result.all()

    def get_by_id(self, org_id: int, owner_id: int) -> Organization | None:
        query = select(Organization).where(
            Organization.id == org_id, Organization.owner_id == owner_id
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
