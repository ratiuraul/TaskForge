from tests.api.test_projects import create_project
from tests.api.test_tasks import create_task
from fastapi import status
from tests.api.test_auth import (
    get_by_email,
    new_user_token,
)
from tests.constants import LOGIN_PAYLOAD


def create_comment(client, auth_token, task_id=None, project_id=None, payload=None):

    if task_id is None:
        if project_id is None:
            project = create_project(client, auth_token)
            project_id = project.json().get("id")
        task = create_task(client=client, auth_token=auth_token, project_id=project_id)
        task_id = task.json().get("id")

    payload = payload or {"body": "Test Comment"}
    return client.post(
        f"/tasks/{task_id}/comments",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=payload,
    )


def test_create_comment(client, auth_token, db):
    response = create_comment(client, auth_token)
    assert response.status_code == status.HTTP_200_OK
    user = get_by_email(db, LOGIN_PAYLOAD["email"])
    assert user.id == response.json().get("author_id")


def test_get_comment(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")
    task = create_task(client=client, auth_token=auth_token, project_id=project_id)
    task_id = task.json().get("id")
    comment1 = create_comment(
        client=client, auth_token=auth_token, task_id=task_id, project_id=project_id
    )
    comment2 = create_comment(
        client=client, auth_token=auth_token, task_id=task_id, project_id=project_id
    )

    response = client.get(
        f"/tasks/{task_id}/comments", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert comment1.json() in response.json()
    assert comment2.json() in response.json()


def test_create_invalid_project(client, auth_token):
    user2_token = new_user_token(client)

    project = create_project(client, user2_token)
    project_id = project.json().get("id")
    user2_task = create_task(
        client=client, auth_token=user2_token, project_id=project_id
    )

    task_id = user2_task.json().get("id")

    comment_response = create_comment(
        client=client, auth_token=auth_token, task_id=task_id, project_id=project_id
    )

    assert comment_response.status_code == status.HTTP_404_NOT_FOUND
    assert comment_response.json() == {"detail": "Project with this id does not exists"}


def test_create_invalid_task_id(client, auth_token):
    project = create_project(client, auth_token)
    project_id = project.json().get("id")

    comment_response = create_comment(
        client=client, auth_token=auth_token, task_id="9999", project_id=project_id
    )
    assert comment_response.status_code == status.HTTP_404_NOT_FOUND
    assert comment_response.json() == {"detail": "Task with this id does not exists"}


def test_delete_comment(client, auth_token):
    comment = create_comment(client, auth_token)
    comment_id = comment.json().get("id")

    delete_response = client.delete(
        f"/comments/{comment_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get(
        f"/comments/{comment_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_create_no_token(client):
    response = create_comment(client, auth_token=None, task_id=1)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


def test_update_comment(client, auth_token):
    comment = create_comment(client, auth_token)
    comment_id = comment.json().get("id")

    response = client.patch(
        f"/comments/{comment_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"body": "updated body"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("body") == "updated body"
