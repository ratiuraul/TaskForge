from fastapi import status
from sqlalchemy import select

from app.common.enums import UserRole
from app.modules.auth.models import User
from tests.constants import (
    LOGIN_PAYLOAD,
    LOGIN_PAYLOAD_2,
    REGISTER_PAYLOAD,
    REGISTER_PAYLOAD_2,
)


def new_user_token(client, register_payload=None, login_payload=None):

    if not register_payload:
        register_payload = REGISTER_PAYLOAD_2

    if not login_payload:
        login_payload = LOGIN_PAYLOAD_2

    client.post("/auth/register", json=register_payload)

    login_response = client.post(
        "/auth/login",
        data={
            "username": login_payload["email"],
            "password": login_payload["password"],
        },
    )
    return login_response.json().get("access_token")


def get_by_email(db, email: str) -> User:
    query = select(User).where(User.email == email)
    return db.scalar(query)


def test_register(client):

    response = client.post(
        "/auth/register",
        json=REGISTER_PAYLOAD,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test@example.com"
    assert response.json()["role"] == UserRole.USER.value


def test_duplicate_email(client):

    client.post("/auth/register", json=REGISTER_PAYLOAD)
    response = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "A user with this email already exists."}


def test_login_success(client):

    client.post("/auth/register", json=REGISTER_PAYLOAD)
    response = client.post(
        "/auth/login",
        data={
            "username": LOGIN_PAYLOAD["email"],
            "password": LOGIN_PAYLOAD["password"],
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()


def test_login_incorrect_password(client):
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    response = client.post(
        "/auth/login",
        data={
            "username": LOGIN_PAYLOAD["email"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Invalid username or password."}


def test_protected_me_route_no_token(client):
    response = client.get("/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_me_route_valid_token(client, auth_token):
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("email") == LOGIN_PAYLOAD["email"]
    assert "password" not in response.json()


def test_protected_me_route_invalid_token(client):

    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}
