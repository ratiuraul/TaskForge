from fastapi import status
from sqlalchemy import select

from app.modules.auth.models.user_model import User
from app.modules.organizations.models.organizations_model import Organization

REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "username": "test",
    "password": "password123",
}

LOGIN_PAYLOAD = {
    "email": "test@example.com",
    "password": "password123",
}


def test_create_org(client):
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    login_response = client.post(
        "/auth/login",
        data={
            "username": LOGIN_PAYLOAD["email"],
            "password": LOGIN_PAYLOAD["password"],
        },
    )
    token = login_response.json().get("access_token")

    response = client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "My Organization",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("name") == "My Organization"
    assert "id" in response.json()
    assert "created_at" in response.json()
    assert "owner_id" not in response.json()


def test_create_org_without_token(client):
    response = client.post(
        "/organizations",
        json={
            "name": "My Organization",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_create_duplicate_org(client):
    client.post("/auth/register", json=REGISTER_PAYLOAD)

    login_response = client.post(
        "/auth/login",
        data={
            "username": LOGIN_PAYLOAD["email"],
            "password": LOGIN_PAYLOAD["password"],
        },
    )
    token = login_response.json().get("access_token")

    client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "My Organization",
        },
    )

    response = client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "My Organization",
        },
    )
    assert response.json() == {"detail": "Organization with this name already exists."}
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_org_sets_current_user_as_owner(client, db):
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    login_response = client.post(
        "/auth/login",
        data={
            "username": LOGIN_PAYLOAD["email"],
            "password": LOGIN_PAYLOAD["password"],
        },
    )
    token = login_response.json().get("access_token")

    response = client.post(
        "/organizations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "My Organization",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    query = select(Organization).where(Organization.id == response.json().get("id"))
    db_org = db.scalar(query)
    user = db.scalar(select(User).where(User.email == REGISTER_PAYLOAD["email"]))
    assert db_org is not None
    assert user is not None
    assert db_org.owner_id == user.id
