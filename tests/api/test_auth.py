from fastapi import status

from app.common.enums import UserRole

REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "username": "test",
    "password": "password123",
}

LOGIN_PAYLOAD = {
    "email": "test@example.com",
    "password": "password123",
}


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


def test_protected_me_route_valid_token(client):
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    login_response = client.post(
        "/auth/login",
        data={
            "username": LOGIN_PAYLOAD["email"],
            "password": LOGIN_PAYLOAD["password"],
        },
    )

    token = login_response.json().get("access_token")

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("email") == LOGIN_PAYLOAD["email"]
    assert "password" not in response.json()


def test_protected_me_route_invalid_token(client):

    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}
