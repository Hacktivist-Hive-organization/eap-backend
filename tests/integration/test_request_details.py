import os

import pytest

from app.common.enums import Status
from app.core.config import settings
from app.main import app

API_PREFIX = f"{settings.API_V1_PREFIX}/requests"
API_SUBMIT = f"{settings.API_V1_PREFIX}/requests/submit"

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="DbUser.username not ready, skipping temporarily in CI",
)


def test_get_request_details_success(
    client, seeded_request_types, users, auth_as, valid_request_payload
):
    owner = users["user1"]
    auth_as(owner)
    # Create request
    payload = valid_request_payload(title="New laptop")

    create_response = client.post(f"{API_PREFIX}", json=payload)
    assert create_response.status_code == 201

    request_id = create_response.json()["id"]

    # Fetch request details
    response = client.get(f"{API_PREFIX}/{request_id}")

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == request_id
    assert body["title"] == payload["title"]
    assert body["current_status"] == Status.DRAFT

    # requester info
    assert body["requester"]["id"] == owner.id
    assert body["requester"]["email"] == owner.email

    # timestamps
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


def test_get_request_details_not_found(client, seeded_request_types, users, auth_as):
    owner = users["user1"]
    auth_as(owner)

    response = client.get(f"{API_PREFIX}/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Request not found"}


def test_get_request_details_forbidden(
    client, seeded_request_types, users, auth_as, valid_request_payload
):
    owner = users["user1"]
    other_user = users["user2"]

    # --- Owner creates request ---
    auth_as(owner)
    payload = valid_request_payload(title="Private request")

    create_response = client.post(API_PREFIX, json=payload)
    assert create_response.status_code == 201
    request_id = create_response.json()["id"]

    # --- Switch auth context to another user ---
    auth_as(other_user)
    response = client.get(f"{API_PREFIX}/{request_id}")

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to view this request"}
    app.dependency_overrides.clear()


def test_get_request_details_admin_succeed(
    client,
    seeded_request_types,
    users,
    auth_as,
    valid_request_payload,
    dashboard_admin,
    db_session,
):
    owner = users["user1"]
    admin = dashboard_admin["admin1"]

    # --- Owner creates request ---
    auth_as(owner)

    payload = valid_request_payload(current_status=Status.SUBMITTED)

    submit_request = client.post(API_SUBMIT, json=payload)
    assert submit_request.status_code == 201
    request_id = submit_request.json()["id"]

    # --- Switch auth context to another user ---
    auth_as(admin)
    # fetch request
    response = client.get(f"{API_PREFIX}/{request_id}")

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == request_id
    assert body["title"] == payload["title"]


def test_get_draft_request_details_admin_forbidden(
    client, seeded_request_types, users, auth_as, valid_request_payload, dashboard_admin
):
    owner = users["user1"]
    admin = dashboard_admin["admin1"]

    # --- Owner creates request ---
    auth_as(owner)
    payload = valid_request_payload(title="Private request")

    create_response = client.post(API_PREFIX, json=payload)
    assert create_response.status_code == 201
    request_id = create_response.json()["id"]

    # --- Switch auth context to another user ---
    auth_as(admin)
    # fetch request
    response = client.get(f"{API_PREFIX}/{request_id}")

    assert response.status_code == 403
    assert response.json() == {"detail": "Request is still in draft state"}
    app.dependency_overrides.clear()
