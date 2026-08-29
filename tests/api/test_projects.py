from fastapi import status

from tests.api.test_org import create_org


def create_project(
    client, auth_token, name="Test Project", description="Test Description", org_id=None
):

    if org_id is None:
        current_org = create_org(client, auth_token, {"name": "Org2"})
        org_id = current_org.json().get("id")

    payload = {
        "name": name,
        "description": description,
        "organization_id": org_id,
    }

    response = client.post(
        "/projects", headers={"Authorization": f"Bearer {auth_token}"}, json=payload
    )

    return response


def test_create_project(client, auth_token):
    response = create_project(client=client, auth_token=auth_token)
    assert response.status_code == status.HTTP_200_OK


def test_create_project_no_auth(client):
    response = create_project(client=client, auth_token="Invalid")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json().get("detail") == "Invalid token"


def test_create_project_invalid_org(client, auth_token):
    response = create_project(client=client, auth_token=auth_token, org_id=666)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "You are not a member of this organization."


def test_create_project_duplicate(client, auth_token):
    project1 = create_project(client=client, auth_token=auth_token)
    response = create_project(
        client=client,
        auth_token=auth_token,
        org_id=project1.json().get("organization_id"),
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        response.json().get("detail")
        == "Project with this name already exists in this organization."
    )


def test_correct_description(client, auth_token):
    response = create_project(client=client, auth_token=auth_token, description=None)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("description") == None
    response2 = create_project(
        client=client,
        auth_token=auth_token,
        name="New Name",
        description="New Description",
        org_id=response.json().get("organization_id"),
    )
    assert response2.status_code == status.HTTP_200_OK
    assert response2.json().get("description") == "New Description"


def test_get_all_project(client, auth_token):
    created_project = create_project(client=client, auth_token=auth_token)
    own_projects_response = client.get(
        "/projects", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert own_projects_response.status_code == status.HTTP_200_OK
    assert created_project.json() in own_projects_response.json()


def test_get_all_no_projects(client, auth_token):
    own_projects_response = client.get(
        "/projects", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert own_projects_response.status_code == status.HTTP_200_OK
    assert own_projects_response.json() == []


def test_get_all_projects_multiple_orgs(client, auth_token):
    org1 = create_org(client, auth_token, {"name": "Org1"})
    org2 = create_org(client, auth_token, {"name": "Org2"})

    project_org_1 = create_project(
        client=client, auth_token=auth_token, org_id=org1.json().get("id")
    )
    project_org_2 = create_project(
        client=client, auth_token=auth_token, org_id=org2.json().get("id")
    )

    response = client.get(
        "/projects", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert project_org_1.json() in response.json()
    assert project_org_2.json() in response.json()


def test_own_projects_only(client, auth_token):
    client.post(
        "/auth/register",
        json={
            "email": "test2@example.com",
            "username": "test2",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "test2@example.com",
            "password": "password123",
        },
    )

    user2_token = login_response.json().get("access_token")

    org_user2 = create_org(
        client, auth_token=user2_token, payload={"name": "Org_user2"}
    )
    org_user2_id = org_user2.json().get("id")

    create_project(client=client, auth_token=user2_token, org_id=org_user2_id)
    projects_user1 = create_project(client, auth_token)

    user1_projects = client.get(
        "/projects", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert user1_projects.json() == [projects_user1.json()]


def test_org_projects_multiple_users(client, auth_token):
    # Todo need to add option to add multiple users to same org
    # 2 useri , aceeasi org, adaugi 2 proiecte la org, get cu fiecare user token, raspunsurile la fel

    user2_email = "test2@example.com"
    client.post(
        "/auth/register",
        json={
            "email": user2_email,
            "username": "test2",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": user2_email,
            "password": "password123",
        },
    )
    user2_token = login_response.json().get("access_token")

    common_org = create_org(client, auth_token, {"name": "Org2"})

    common_org_id = common_org.json().get("id")

    # add user2 to common_org
    client.post(
        f"/organizations/{common_org_id}/members",
        json={"email": user2_email, "role": "MEMBER"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    project1 = create_project(
        client, auth_token, name="Project1", description="PJ1desc", org_id=common_org_id
    )
    project2 = create_project(
        client, auth_token, name="Project2", description="PJ2desc", org_id=common_org_id
    )

    user1_projects = client.get(
        "/projects", headers={"Authorization": f"Bearer {auth_token}"}
    )

    user2_projects = client.get(
        "/projects", headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert (
        user1_projects.json()
        == user2_projects.json()
        == [project1.json(), project2.json()]
    )
    assert len(user1_projects.json()) == len(user2_projects.json()) == 2
