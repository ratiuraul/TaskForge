from constants import LOGIN_PAYLOAD_2
from fastapi import status
from sqlalchemy import select

from app.modules.projects.models import Project
from tests.api.test_auth import new_user_token
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
    user2_token = new_user_token(client)

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

    user2_token = new_user_token(client)

    common_org = create_org(client, auth_token, {"name": "Org2"})

    common_org_id = common_org.json().get("id")

    # add user2 to common_org
    client.post(
        f"/organizations/{common_org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": "MEMBER"},
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


def test_get_project_by_id(client, auth_token):
    created_project = create_project(client=client, auth_token=auth_token)
    project_id = created_project.json().get("id")
    own_projects_response = client.get(
        f"/projects/{project_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert own_projects_response.status_code == status.HTTP_200_OK
    assert created_project.json() == own_projects_response.json()


def test_get_invalid_project_id(client, auth_token):
    invalid_project_response = client.get(
        "/projects/99999999", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert invalid_project_response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        invalid_project_response.json().get("detail")
        == "Project with this id does not exists"
    )


def test_different_project_org(client, auth_token):
    user2_token = new_user_token(client)

    org2 = create_org(client, user2_token, {"name": "Org2"})

    org2_id = org2.json().get("id")

    org2_project = create_project(client=client, auth_token=user2_token, org_id=org2_id)

    org2_project_id = org2_project.json().get("id")

    get_org_2_project = client.get(
        f"/projects/{org2_project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert get_org_2_project.status_code == status.HTTP_404_NOT_FOUND
    assert (
        get_org_2_project.json().get("detail")
        == "You are not a member of this organization."
    )


def test_get_project_no_auth(client):
    no_auth_response = client.get("/projects/10")
    assert no_auth_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert no_auth_response.json().get("detail") == "Not authenticated"


def test_update_name(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "New Name"},
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json().get("name") == "New Name"


def test_update_description(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"description": "New Description"},
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json().get("description") == "New Description"


def test_update_organization_id(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    new_org = create_org(client, auth_token, {"name": "New Org"})
    new_org_id = new_org.json().get("id")

    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"organization_id": new_org_id},
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json().get("organization_id") == new_org_id


def test_update(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    new_org = create_org(client, auth_token, {"name": "New Org"})
    new_org_id = new_org.json().get("id")

    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "organization_id": new_org_id,
            "name": "New Name",
            "description": "New Description",
        },
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json().get("organization_id") == new_org_id
    assert update_response.json().get("name") == "New Name"
    assert update_response.json().get("description") == "New Description"


def test_patch_no_payload(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={},
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json() == project.json()


def test_patch_invalid_project(client, auth_token):
    update_response = client.patch(
        "/projects/9999",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={},
    )
    assert update_response.status_code == status.HTTP_404_NOT_FOUND
    assert update_response.json() == {"detail": "Project with this id does not exists"}


def test_invalid_user(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    user2_token = new_user_token(client)

    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
        json={},
    )

    assert update_response.status_code == status.HTTP_404_NOT_FOUND
    assert update_response.json() == {"detail": "Project with this id does not exists"}


def test_already_exists_in_new_org(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    project_name = project.json().get("name")

    new_org = create_org(client, auth_token, {"name": "New Org"})
    new_org_id = new_org.json().get("id")
    create_project(client, auth_token, name=project_name, org_id=new_org_id)

    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"organization_id": new_org_id},
    )

    assert update_response.status_code == status.HTTP_409_CONFLICT
    assert update_response.json() == {
        "detail": "Project with this name already exists in this organization."
    }


def test_update_project_same_name_and_org_id(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    project_name = project.json().get("name")
    org_id = project.json().get("organization_id")

    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "project_name": project_name,
            "org_id": org_id,
            "description": "New Description",
        },
    )
    assert update_response.status_code == status.HTTP_200_OK


def test_move_to_no_membership_org(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    user2_token = new_user_token(client)

    new_org = create_org(client, user2_token, {"name": "New Org"})
    new_org_id = new_org.json().get("id")
    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "organization_id": new_org_id,
        },
    )

    assert update_response.status_code == status.HTTP_404_NOT_FOUND
    assert update_response.json() == {
        "detail": "You are not a member of this organization."
    }


def test_move_to_membership_org(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    new_org = create_org(client, auth_token, {"name": "New Org"})
    new_org_id = new_org.json().get("id")
    update_response = client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "organization_id": new_org_id,
        },
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json().get("organization_id") == new_org_id


def test_update_validate_db(client, auth_token, db):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    new_org = create_org(client, auth_token, {"name": "New Org"})
    new_org_id = new_org.json().get("id")
    client.patch(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "New Name",
            "description": "New Description",
            "organization_id": new_org_id,
        },
    )
    query = select(Project).where(Project.id == project_id)
    db_response = db.scalar(query)
    assert db_response.name == "New Name"
    assert db_response.description == "New Description"
    assert db_response.organization_id == new_org_id


def test_delete_success(client, auth_token, db):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    project_exists = db.scalar(select(Project).where(Project.id == project_id))

    assert project_exists is not None

    delete_response = client.delete(
        f"/projects/{project_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    project_does_not_exist = db.scalar(select(Project).where(Project.id == project_id))

    assert project_does_not_exist is None


def test_project_not_in_get_all(client, auth_token):

    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    get_projects = client.get(
        "/projects", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert project.json() in get_projects.json()

    client.delete(
        f"/projects/{project_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )

    get_projects = client.get(
        "/projects", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert project.json() not in get_projects.json()


def test_delete_no_auth(client, auth_token):

    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    delete_response = client.delete(
        f"/projects/{project_id}", headers={"Authorization": "Bearer invalid_token"}
    )

    assert delete_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert delete_response.json() == {"detail": "Invalid token"}


def test_delete_invalid_id(client, auth_token):

    delete_response = client.delete(
        f"/projects/9999", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert delete_response.status_code == status.HTTP_404_NOT_FOUND
    assert delete_response.json() == {"detail": "Project with this id does not exists"}
