from constants import LOGIN_PAYLOAD_2, LOGIN_PAYLOAD_3, REGISTER_PAYLOAD_3
from fastapi import status

from app.common.enums import OrganizationRole
from tests.api.test_auth import new_user_token
from tests.api.test_org import create_org


def test_owner_adds_member(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")
    new_user_token(client)

    response = client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == status.HTTP_200_OK


def test_member_user_cannot_add(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")
    member1_token = new_user_token(client)
    new_user_token(
        client, register_payload=REGISTER_PAYLOAD_3, login_payload=LOGIN_PAYLOAD_3
    )

    # owner adds admin to org
    admin_response = client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert admin_response.status_code == status.HTTP_200_OK

    # member1 adds member2 to org
    user_response = client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_3.get("email"), "role": OrganizationRole.ADMIN},
        headers={"Authorization": f"Bearer {member1_token}"},
    )
    assert user_response.status_code == status.HTTP_403_FORBIDDEN
    assert user_response.json() == {"detail": "User is not authorized for this action"}


def test_admin_adds_member(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")
    admin_token = new_user_token(client)
    new_user_token(
        client, register_payload=REGISTER_PAYLOAD_3, login_payload=LOGIN_PAYLOAD_3
    )

    # owner adds admin to org
    admin_response = client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.ADMIN},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert admin_response.status_code == status.HTTP_200_OK

    # admin adds user to org
    user_response = client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_3.get("email"), "role": OrganizationRole.ADMIN},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert user_response.status_code == status.HTTP_200_OK


def test_non_member_cannot_add_member(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")

    user1_token = new_user_token(client)
    new_user_token(
        client, register_payload=REGISTER_PAYLOAD_3, login_payload=LOGIN_PAYLOAD_3
    )

    response = client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_3.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Organization with this id does not exists"}


def test_add_user_twice(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")

    new_user_token(client)

    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    response = client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "User is already member in this organization."}


def test_add_non_existing_user(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")

    response = client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Invalid User id."}


def test_add_to_non_existing_org(client, auth_token):
    create_org(client, auth_token, {"name": "Org1"})
    new_user_token(client)

    response = client.post(
        "/organizations/999/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Organization with this id does not exists"}


def test_add_no_auth(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")

    new_user_token(client)

    response = client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid token'}
