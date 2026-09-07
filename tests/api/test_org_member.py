from constants import (
    LOGIN_PAYLOAD_2,
    LOGIN_PAYLOAD_3,
    REGISTER_PAYLOAD_2,
    REGISTER_PAYLOAD_3,
)
from fastapi import status

from app.common.enums import OrganizationRole
from tests.api.test_auth import get_by_email, new_user_token
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
    assert response.json() == {"detail": "Invalid token"}


def test_owner_deletes_admin_and_member(client, auth_token, db):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")

    # admin user
    new_user_token(client, REGISTER_PAYLOAD_2, LOGIN_PAYLOAD_2)
    admin_user = get_by_email(db, REGISTER_PAYLOAD_2.get("email"))
    admin_user_id = admin_user.id
    # member user
    new_user_token(client, REGISTER_PAYLOAD_3, LOGIN_PAYLOAD_3)
    member_user = get_by_email(db, REGISTER_PAYLOAD_3.get("email"))
    member_user_id = member_user.id
    # add admin to org
    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.ADMIN},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # add member to org
    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_3.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # owner deletes admin
    resp1 = client.delete(
        f"/organizations/{org_id}/members/{admin_user_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp1.status_code == status.HTTP_204_NO_CONTENT

    # owner deletes member
    resp2 = client.delete(
        f"/organizations/{org_id}/members/{member_user_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp2.status_code == status.HTTP_204_NO_CONTENT


def test_admin_deletes_member(client, auth_token, db):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")

    # admin user
    admin_token = new_user_token(client, REGISTER_PAYLOAD_2, LOGIN_PAYLOAD_2)
    admin_user = get_by_email(db, REGISTER_PAYLOAD_2.get("email"))
    admin_user_id = admin_user.id

    # member user
    new_user_token(client, REGISTER_PAYLOAD_3, LOGIN_PAYLOAD_3)
    member_user = get_by_email(db, REGISTER_PAYLOAD_3.get("email"))
    member_user_id = member_user.id

    # add admin to org
    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.ADMIN},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # add member to org
    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_3.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    resp1 = client.delete(
        f"/organizations/{org_id}/members/{member_user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp1.status_code == status.HTTP_204_NO_CONTENT


def test_normal_member_cannot_remove(client, auth_token, db):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")

    # member user 1
    member_user1_token = new_user_token(client, REGISTER_PAYLOAD_2, LOGIN_PAYLOAD_2)

    # member user
    new_user_token(client, REGISTER_PAYLOAD_3, LOGIN_PAYLOAD_3)
    member_user = get_by_email(db, REGISTER_PAYLOAD_3.get("email"))
    member_user_id = member_user.id

    # add member1 to org
    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # add member to org
    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_3.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    resp1 = client.delete(
        f"/organizations/{org_id}/members/{member_user_id}",
        headers={"Authorization": f"Bearer {member_user1_token}"},
    )
    assert resp1.status_code == status.HTTP_403_FORBIDDEN
    assert resp1.json() == {"detail": "User is not authorized for this action"}


def test_cannot_delete_user_from_another_org(client, auth_token, db):
    org_admin_token = new_user_token(client, REGISTER_PAYLOAD_2, LOGIN_PAYLOAD_2)
    org = create_org(client, org_admin_token, {"name": "Org2"})
    org_id = org.json().get("id")
    admin_user = get_by_email(db, REGISTER_PAYLOAD_2.get("email"))
    admin_user_id = admin_user.id
    resp1 = client.delete(
        f"/organizations/{org_id}/members/{admin_user_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp1.status_code == status.HTTP_404_NOT_FOUND
    assert resp1.json() == {"detail": "Organization with this id does not exists"}


def test_delete_no_auth(client, auth_token, db):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")

    new_user_token(client, REGISTER_PAYLOAD_3, LOGIN_PAYLOAD_3)
    member_user = get_by_email(db, REGISTER_PAYLOAD_3.get("email"))
    member_user_id = member_user.id

    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_3.get("email"), "role": OrganizationRole.MEMBER},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    resp2 = client.delete(
        f"/organizations/{org_id}/members/{member_user_id}",
        headers={"Authorization": f"Bearer invalid_token"},
    )
    assert resp2.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp2.json() == {"detail": "Invalid token"}


def test_delete_invalid_user(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")
    resp2 = client.delete(
        f"/organizations/{org_id}/members/99999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp2.status_code == status.HTTP_404_NOT_FOUND
    assert resp2.json() == {"detail": "Invalid User id."}


def test_any_user_can_see_members_of_own_org(client, auth_token):
    org = create_org(client, auth_token, {"name": "Org1"})
    org_id = org.json().get("id")

    # create users
    admin_user_token = new_user_token(client, REGISTER_PAYLOAD_2, LOGIN_PAYLOAD_2)
    member_user_token = new_user_token(client, REGISTER_PAYLOAD_3, LOGIN_PAYLOAD_3)
    no_member_user_token = new_user_token(
        client,
        {
            "email": "test4@example.com",
            "username": "test4",
            "password": "password123",
        },
        {
            "email": "test4@example.com",
            "password": "password123",
        },
    )

    # add admin and member to org
    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_2.get("email"), "role": OrganizationRole.ADMIN},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    client.post(
        f"/organizations/{org_id}/members",
        json={"email": LOGIN_PAYLOAD_3.get("email"), "role": OrganizationRole.ADMIN},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    unauthorized_members_response = client.get(
        f"/organizations/{org_id}/members",
        headers={"Authorization": f"Bearer invalid_token"},
    )

    assert unauthorized_members_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert unauthorized_members_response.json() == {"detail": "Invalid token"}

    owner_members_response = client.get(
        f"/organizations/{org_id}/members",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert owner_members_response.status_code == status.HTTP_200_OK
    assert len(owner_members_response.json()) == 3

    admin_members_response = client.get(
        f"/organizations/{org_id}/members",
        headers={"Authorization": f"Bearer {admin_user_token}"},
    )

    assert admin_members_response.status_code == status.HTTP_200_OK
    assert len(admin_members_response.json()) == 3

    member_members_response = client.get(
        f"/organizations/{org_id}/members",
        headers={"Authorization": f"Bearer {member_user_token}"},
    )

    assert member_members_response.status_code == status.HTTP_200_OK
    assert len(member_members_response.json()) == 3

    no_member_response = client.get(
        f"/organizations/{org_id}/members",
        headers={"Authorization": f"Bearer {no_member_user_token}"},
    )
    assert no_member_response.status_code == status.HTTP_404_NOT_FOUND
    assert no_member_response.json() == {
        "detail": "Organization with this id does not exists"
    }
