from fastapi import status
from sqlalchemy import select

from app.common.enums import OrganizationRole
from app.modules.auth.models.user_model import User
from app.modules.organizations.models.organizations_model import (
    Organization,
    OrganizationMember,
)
from tests.constants import REGISTER_PAYLOAD


def create_org(client, auth_token, payload):
    return client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=payload,
    )


def test_create_org(client, auth_token):
    response = client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "My Organization",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("name") == "My Organization"
    assert "id" in response.json()
    assert "created_at" in response.json()


def test_create_org_without_token(client):
    response = client.post(
        "/organizations",
        json={
            "name": "My Organization",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_create_duplicate_org(client, auth_token):

    client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "My Organization",
        },
    )

    response = client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "My Organization",
        },
    )
    assert response.json() == {"detail": "Organization with this name already exists."}
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_org_creates_owner_membership(client, db, auth_token):
    response = client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "My Organization",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    query = select(Organization).where(Organization.id == response.json().get("id"))
    db_org = db.scalar(query)
    assert db_org is not None
    user = db.scalar(select(User).where(User.email == REGISTER_PAYLOAD["email"]))
    assert user is not None
    org_member_query = (
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == response.json().get("id"))
        .where(OrganizationMember.user_id == user.id)
    )
    org_member = db.scalar(org_member_query)
    assert org_member is not None
    assert org_member.role == OrganizationRole.OWNER


def test_get_all_empty_orgs(client, auth_token):
    no_orgs_response = client.get(
        "/organizations", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert no_orgs_response.status_code == status.HTTP_200_OK
    assert no_orgs_response.json() == []


def test_get_returns_multiple_orgs(client, auth_token):
    org1 = create_org(client, auth_token, {"name": "Org1"})
    org1_resp = client.get(
        "/organizations", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert org1_resp.status_code == status.HTTP_200_OK
    assert isinstance(org1_resp.json(), list)
    assert org1_resp.json() == [org1.json()]
    org2 = create_org(client, auth_token, {"name": "Org2"})
    orgs_resp = client.get(
        "/organizations", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert orgs_resp.json() == [org1.json(), org2.json()]


def test_multiple_users_orgs(client, auth_token):
    org_user1 = create_org(client, auth_token, {"name": "Org_user_1"})
    client.post(
        "/auth/register",
        json={
            "email": "test2@example.com",
            "username": "test2",
            "password": "password123",
        },
    )

    token_user_2 = (
        client.post(
            "/auth/login",
            data={
                "username": "test2@example.com",
                "password": "password123",
            },
        )
        .json()
        .get("access_token")
    )

    org_user2 = create_org(client, token_user_2, {"name": "Org_user_2"})

    orgs_user1 = client.get(
        "/organizations", headers={"Authorization": f"Bearer {auth_token}"}
    )
    orgs_user2 = client.get(
        "/organizations", headers={"Authorization": f"Bearer {token_user_2}"}
    )

    assert orgs_user1.json() == [org_user1.json()]
    assert orgs_user2.json() == [org_user2.json()]


def test_get_all_no_auth(client):
    response = client.get(
        "/organizations", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_get_org_with_id(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org_user_1"})
    org_id = org.json().get("id")
    get_by_id_resp = client.get(
        f"/organizations/{org_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_by_id_resp.status_code == status.HTTP_200_OK
    assert isinstance(get_by_id_resp.json(), dict)
    assert org_id == get_by_id_resp.json().get("id")
    assert "Org_user_1" == get_by_id_resp.json().get("name")


def test_get_org_invalid_id(client, auth_token):
    get_by_id_resp = client.get(
        "/organizations/9999", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_by_id_resp.status_code == status.HTTP_404_NOT_FOUND
    assert get_by_id_resp.json() == {
        "detail": "Organization with this id does not exists"
    }


def test_get_other_users_org(client, auth_token):
    org_user1 = create_org(client, auth_token, {"name": "Org_user_1"})
    client.post(
        "/auth/register",
        json={
            "email": "test2@example.com",
            "username": "test2",
            "password": "password123",
        },
    )

    token_user_2 = (
        client.post(
            "/auth/login",
            data={
                "username": "test2@example.com",
                "password": "password123",
            },
        )
        .json()
        .get("access_token")
    )

    org_user_1 = client.get(
        f"/organizations/{org_user1.json().get('id')}",
        headers={"Authorization": f"Bearer {token_user_2}"},
    )
    assert org_user_1.status_code == status.HTTP_404_NOT_FOUND
    assert org_user_1.json() == {"detail": "Organization with this id does not exists"}


def test_patch_org(client, auth_token, db):
    org = create_org(client, auth_token, {"name": "Org_user_1"})
    org_id = org.json().get("id")
    update_org = client.patch(
        f"/organizations/{org_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Updated Name"},
    )
    assert update_org.status_code == 200
    assert update_org.json()["name"] == "Updated Name"
    db_org = db.scalar(select(Organization).where(Organization.id == org_id))

    assert db_org.name == "Updated Name"


def test_patch_duplicate_name(client, auth_token, db):
    org1 = create_org(client, auth_token, {"name": "Org_user_1"})
    create_org(client, auth_token, {"name": "Org_user_2"})

    org1_id = org1.json().get("id")
    update_org = client.patch(
        f"/organizations/{org1_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Org_user_2"},
    )

    assert update_org.status_code == status.HTTP_409_CONFLICT
    assert update_org.json() == {
        "detail": "Organization with this name already exists."
    }

    db_org = db.scalar(select(Organization).where(Organization.id == org1_id))
    assert db_org.name == "Org_user_1"


def test_patch_org_invalid_id(client, auth_token):
    update_org = client.patch(
        "/organizations/99999",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Org_user_2"},
    )
    assert update_org.status_code == status.HTTP_404_NOT_FOUND
    assert update_org.json() == {"detail": "Organization with this id does not exists"}


def test_patch_another_users_org(client, auth_token):
    org_user1 = create_org(client, auth_token, {"name": "Org_user_1"})
    org_user1_id = org_user1.json().get("id")
    client.post(
        "/auth/register",
        json={
            "email": "test2@example.com",
            "username": "test2",
            "password": "password123",
        },
    )

    token_user_2 = (
        client.post(
            "/auth/login",
            data={
                "username": "test2@example.com",
                "password": "password123",
            },
        )
        .json()
        .get("access_token")
    )

    patch_response = client.patch(
        f"/organizations/{org_user1_id}",
        headers={"Authorization": f"Bearer {token_user_2}"},
        json={"name": "New Name"},
    )
    assert patch_response.status_code == status.HTTP_404_NOT_FOUND
    assert patch_response.json() == {
        "detail": "Organization with this id does not exists"
    }


def test_patch_no_auth(client):
    response = client.patch(
        "/organizations/999",
        headers={"Authorization": "Bearer invalid_token"},
        json={"name": "New Name"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_delete_existing_org(client, auth_token, db):
    org_user1 = create_org(client, auth_token, {"name": "Org_user_1"})
    org_user1_id = org_user1.json().get("id")
    delete_response = client.delete(
        f"/organizations/{org_user1_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    db_org = db.scalar(select(Organization).where(Organization.id == org_user1_id))
    assert db_org is None
    db_org_member = db.scalar(
        select(OrganizationMember).where(OrganizationMember.id == org_user1_id)
    )
    assert db_org_member is None


def test_delete_invalid_id(client, auth_token):
    delete_response = client.delete(
        "/organizations/9999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert delete_response.status_code == status.HTTP_404_NOT_FOUND
    assert delete_response.json() == {
        "detail": "Organization with this id does not exists"
    }


def test_delete_other_users_org(client, auth_token):
    org_user1 = create_org(client, auth_token, {"name": "Org_user_1"})
    org_user1_id = org_user1.json().get("id")
    client.post(
        "/auth/register",
        json={
            "email": "test2@example.com",
            "username": "test2",
            "password": "password123",
        },
    )

    token_user_2 = (
        client.post(
            "/auth/login",
            data={
                "username": "test2@example.com",
                "password": "password123",
            },
        )
        .json()
        .get("access_token")
    )

    delete_response = client.delete(
        f"/organizations/{org_user1_id}",
        headers={"Authorization": f"Bearer {token_user_2}"},
    )

    assert delete_response.status_code == status.HTTP_404_NOT_FOUND
    assert delete_response.json() == {
        "detail": "Organization with this id does not exists"
    }


def test_delete_no_token(client):
    response = client.delete(
        "/organizations/999", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_exactly_one_owner(client, auth_token, db):
    response = client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "My Organization",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    user = db.scalar(select(User).where(User.email == REGISTER_PAYLOAD["email"]))
    assert user is not None

    members = db.scalars(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == response.json().get("id"))
        .where(OrganizationMember.user_id == user.id)
    ).all()
    assert len(members) == 1
    assert members[0].role == OrganizationRole.OWNER
