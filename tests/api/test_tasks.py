from starlette.status import HTTP_200_OK
from sqlalchemy import select
from tests.api.test_projects import create_project
from fastapi import status
from app.modules.tasks.models import Task
from app.common.enums import OrganizationRole, TaskPriority, TaskStatus
from tests.api.test_auth import (
    get_by_email,
    new_user_token,
)
from tests.api.test_org import create_org
from tests.constants import (
    LOGIN_PAYLOAD,
    LOGIN_PAYLOAD_2,
    LOGIN_PAYLOAD_3,
    REGISTER_PAYLOAD_3,
)


def create_task(client, auth_token, project_id, payload=None):
    payload = payload or {"title": "Test Task"}
    return client.post(
        f"/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=payload,
    )


def test_create_task(client, auth_token, db):
    project = create_project(client, auth_token)

    project_id = project.json().get("id")
    response = create_task(client, auth_token, project_id)

    assert response.status_code == status.HTTP_200_OK
    user = get_by_email(db, LOGIN_PAYLOAD["email"])
    assert response.json()["created_by_id"] == user.id
    assert all(
        [
            key in response.json()
            for key in ["id", "title", "project_id", "created_by_id"]
        ]
    )


def test_create_no_auth_token(client):
    response = create_task(client=client, auth_token=None, project_id=None)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_create_invalid_token(client):
    response = create_task(client=client, auth_token="invalid_token", project_id=None)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_create_defults(client, auth_token):
    project = create_project(client, auth_token)

    project_id = project.json().get("id")
    response = create_task(client, auth_token, project_id)

    assert response.json().get("priority") == "low"
    assert response.json().get("status") == "draft"


def test_create_invalid_project_id(client, auth_token):

    response = create_task(client, auth_token, 999999)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with this id does not exists"}


def test_create_task_user_not_in_org(client, auth_token):
    user2_token = new_user_token(client)
    project = create_project(client, auth_token)

    project_id = project.json().get("id")
    response = create_task(client, user2_token, project_id)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with this id does not exists"}


def test_create_assigned_task(client, auth_token, db):
    project = create_project(client, auth_token)

    project_id = project.json().get("id")

    user = get_by_email(db, LOGIN_PAYLOAD["email"])
    user_id = user.id
    response = create_task(
        client,
        auth_token,
        project_id,
        payload={"title": "Test Task", "assigned_to_id": user_id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("assigned_to_id") == user_id


def test_assign_to_user_not_in_org(client, auth_token, db):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    new_user_token(client)
    user = get_by_email(db, LOGIN_PAYLOAD_2["email"])
    user_id = user.id

    response = create_task(
        client,
        auth_token,
        project_id,
        payload={"title": "Test Task", "assigned_to_id": user_id},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Asignee id is not valid."}


def test_fake_created_by_id(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    fake_id = 9999999
    response = create_task(
        client,
        auth_token,
        project_id,
        payload={"title": "Test Task", "created_by_id": fake_id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("created_by_id")
    assert response.json().get("created_by_id") != fake_id


def test_get_tasks(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    response = client.get(
        f"/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_tasks_no_auth_token(client):
    response = client.get(
        f"/projects/999/tasks",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_get_tasks_no_auth_token(client):
    response = client.get(
        f"/projects/999/tasks",
        headers={"Authorization": f"Bearer invalid_token"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_get_created_tasks(client, auth_token):

    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task1 = create_task(client, auth_token, project_id, {"title": "Task1"})

    task2 = create_task(client, auth_token, project_id, {"title": "Task2"})

    response = client.get(
        f"/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert task1.json() in response.json()
    assert task2.json() in response.json()


def test_get_created_tasks_invalid_project(client, auth_token):
    response = client.get(
        f"/projects/9999/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with this id does not exists"}


def test_get_created_tasks_scoped_to_project(client, auth_token):

    project_1 = create_project(client, auth_token, name="Project 1")
    project_1_id = project_1.json().get("id")

    project_2 = create_project(client, auth_token, name="Project 2")
    project_2_id = project_2.json().get("id")

    task1 = create_task(client, auth_token, project_1_id, {"title": "Task1"})

    response_1 = client.get(
        f"/projects/{project_1_id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response_1.status_code == HTTP_200_OK
    assert task1.json() in response_1.json()

    response_2 = client.get(
        f"/projects/{project_2_id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response_2.status_code == HTTP_200_OK
    assert task1.json() not in response_2.json()


def test_get_tasks_other_users_project(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    user2_token = new_user_token(client)

    response = client.get(
        f"/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {user2_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with this id does not exists"}


def test_patch_taks_title(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    new_title = "New Title"

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": f"{new_title}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("title") == new_title


def test_patch_taks_status_priority(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    response1 = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"priority": "Invalid Priority"},
    )

    assert response1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert task.json().get("priority") == TaskPriority.LOW

    response2 = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"priority": TaskPriority.HIGH},
    )

    assert response2.status_code == status.HTTP_200_OK
    assert response2.json().get("priority") == TaskPriority.HIGH

    response3 = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"status": "Invalid Status"},
    )

    assert response3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert task.json().get("status") == TaskStatus.DRAFT

    response4 = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"status": TaskStatus.DONE},
    )

    assert response4.status_code == status.HTTP_200_OK
    assert response4.json().get("status") == TaskStatus.DONE


def test_patch_empty_payload(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == task.json()


def test_patch_no_auth_token(client):
    response = client.patch(
        "/tasks/999",
        json={},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_patch_invalid_task_id(client, auth_token):
    response = client.patch(
        "/tasks/99999", headers={"Authorization": f"Bearer {auth_token}"}, json={}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Task with this id does not exists"}


def test_patch_other_users_task(client, auth_token):
    user2_token = new_user_token(client)
    project = create_project(client, auth_token)

    project_id = project.json().get("id")
    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
        json={"title": f"New Title"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with this id does not exists"}


def test_patch_assign_to_org_member(client, auth_token, db):
    project = create_project(client, auth_token)

    project_id = project.json().get("id")
    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    org_id = project.json().get("organization_id")

    new_user_token(client)
    user2 = get_by_email(db, LOGIN_PAYLOAD_2["email"])
    user2_id = user2.id

    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"assigned_to_id": f"{user2_id}"},
    )

    assert response.status_code == status.HTTP_200_OK


def test_patch_assign_to_non_org_member(client, auth_token, db):
    project = create_project(client, auth_token)

    project_id = project.json().get("id")
    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    new_user_token(client)
    user2 = get_by_email(db, LOGIN_PAYLOAD_2["email"])
    user2_id = user2.id

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"assigned_to_id": f"{user2_id}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Asignee id is not valid."}


def test_move_task_to_users_project(client, auth_token):
    project_1 = create_project(client, auth_token)
    project_1_id = project_1.json().get("id")
    project_2 = create_project(client, auth_token, name="New Project")
    project_2_id = project_2.json().get("id")

    task = create_task(client, auth_token, project_1_id)
    task_id = task.json().get("id")

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"project_id": f"{project_2_id}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("project_id") == project_2_id


def test_move_task_to_non_users_project(client, auth_token):
    project_1 = create_project(client, auth_token)
    project_1_id = project_1.json().get("id")

    user2_token = new_user_token(client)
    org_user2 = create_org(client, user2_token, {"name": "Different Org"})

    project_2 = create_project(client, user2_token, org_id=org_user2.json().get("id"))
    project_2_id = project_2.json().get("id")

    task = create_task(client, auth_token, project_1_id)
    task_id = task.json().get("id")

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"project_id": f"{project_2_id}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with this id does not exists"}


def test_move_task_assignee_not_in_target_project(client, auth_token, db):
    org_1 = create_org(client, auth_token, {"name": "Org 1"})
    org_1_id = org_1.json().get("id")

    project_1 = create_project(client, auth_token, name="Project 1", org_id=org_1_id)
    project_1_id = project_1.json().get("id")

    new_user_token(client, REGISTER_PAYLOAD_3, LOGIN_PAYLOAD_3)
    user3 = get_by_email(db, LOGIN_PAYLOAD_3["email"])
    user3_id = user3.id

    client.post(
        f"/organizations/{org_1_id}/members",
        json={"email": LOGIN_PAYLOAD_3["email"], "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    org_2 = create_org(client, auth_token, {"name": "Org 2"})
    org_2_id = org_2.json().get("id")

    project_2 = create_project(client, auth_token, name="Project 2", org_id=org_2_id)
    project_2_id = project_2.json().get("id")

    task = create_task(
        client,
        auth_token,
        project_1_id,
        payload={"title": "Task Title", "assigned_to_id": user3_id},
    )
    task_id = task.json().get("id")

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"project_id": project_2_id},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Asignee id is not valid."}


def test_get_task_by_id(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    created_task = create_task(client, auth_token, project_id)
    task_id = created_task.json().get("id")

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert created_task.json() == response.json()


def test_get_invalid_task_id(client, auth_token):
    response = client.get(
        "/tasks/99999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Task with this id does not exists"


def test_get_other_users_task(client, auth_token):
    user2_token = new_user_token(client)
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Project with this id does not exists"


def test_get_task_no_auth(client):
    response = client.get("/tasks/10")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json().get("detail") == "Not authenticated"


def test_delete_task(client, auth_token, db):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    task_exists = db.scalar(select(Task).where(Task.id == task_id))
    assert task_exists is not None

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    task_does_not_exist = db.scalar(select(Task).where(Task.id == task_id))
    assert task_does_not_exist is None


def test_delete_task_not_in_list(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    get_tasks = client.get(
        f"/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert task.json() in get_tasks.json()

    client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    get_tasks = client.get(
        f"/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert task.json() not in get_tasks.json()


def test_delete_no_auth_token(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    delete_response = client.delete(f"/tasks/{task_id}")

    assert delete_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert delete_response.json() == {"detail": "Not authenticated"}


def test_delete_invalid_token(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert delete_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert delete_response.json() == {"detail": "Invalid token"}


def test_delete_invalid_task_id(client, auth_token):
    delete_response = client.delete(
        "/tasks/99999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert delete_response.status_code == status.HTTP_404_NOT_FOUND
    assert delete_response.json() == {"detail": "Task with this id does not exists"}


def test_delete_other_users_task(client, auth_token, db):
    user2_token = new_user_token(client)
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task = create_task(client, auth_token, project_id)
    task_id = task.json().get("id")

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
    )

    assert delete_response.status_code == status.HTTP_404_NOT_FOUND
    assert delete_response.json() == {"detail": "Project with this id does not exists"}

    task_still_exists = db.scalar(select(Task).where(Task.id == task_id))
    assert task_still_exists is not None


def test_get_tasks_query_params(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    task1 = create_task(
        client,
        auth_token,
        project_id,
        payload={"title": "Task 1", "status": TaskStatus.DONE},
    )

    create_task(
        client,
        auth_token,
        project_id,
        payload={"title": "Task 2", "status": TaskStatus.IN_PROGRESS},
    )

    response = client.get(
        f"/projects/{project_id}/tasks?status={TaskStatus.DONE.value}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [task1.json()]
