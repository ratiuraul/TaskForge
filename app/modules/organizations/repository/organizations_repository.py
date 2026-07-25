from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.organizations.models import Organization


class OrganizationsRepository:
    def __init__(self, db: Session, user: User):
        self.db = db

    def create(self, organization: Organization) -> Organization:
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def get_all_by_owner(self, owner_id) -> list[Organization]:
        query = select(Organization).where(Organization.owner_id == owner_id)
        result = self.db.scalars(query)
        return result.all()

    def get_by_id(self, org_id: int) -> Organization | None:
        query = select(Organization).where(Organization.id == org_id)
        return self.db.scalar(query)
