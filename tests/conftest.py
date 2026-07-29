import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.dependencies import get_db
from app.main import app
from tests.constants import LOGIN_PAYLOAD, REGISTER_PAYLOAD

test_engine = create_engine(settings.TEST_DATABASE_URL, echo=True)

TestingSessionLocal = sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture
def db():
    connection = test_engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app=app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def auth_token(client):
    register = client.post("/auth/register", json=REGISTER_PAYLOAD)

    assert register.status_code == status.HTTP_200_OK

    login_response = client.post(
        "/auth/login",
        data={
            "username": LOGIN_PAYLOAD["email"],
            "password": LOGIN_PAYLOAD["password"],
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    return login_response.json().get("access_token")
