from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.common.enums import OrganizationRole
from app.modules.organizations.models.organizations_model import OrganizationMember


class OrganizationMembersRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, organization_member: OrganizationMember) -> OrganizationMember:
        self.db.add(organization_member)
        self.db.commit()
        self.db.refresh(organization_member)
        return organization_member

    def get_membership(
        self, organization_id: int, user_id: int
    ) -> OrganizationMember | None:
        query = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
            .where(OrganizationMember.user_id == user_id)
        )
        result = self.db.scalar(query)
        return result

    def get_owner(self, organization_id: int) -> OrganizationMember | None:
        query = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
            .where(OrganizationMember.role == OrganizationRole.OWNER)
        )
        return self.db.scalar(query)

    def delete_by_organization(self, organization_id):
        query = delete(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id
        )
        self.db.execute(query)
        self.db.commit()

    def delete_by_user_and_org_id(self, organization_id, user_id):
        query = (
            delete(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
            .where(OrganizationMember.user_id == user_id)
        )
        self.db.execute(query)
        self.db.commit()
