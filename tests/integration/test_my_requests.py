# tests/integration/test_my_requests.py

import os

import pytest

from app.common.enums import Status
from app.core.config import settings

API_PREFIX = f"{settings.API_V1_PREFIX}/requests"

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="DbUser.username not ready, skipping temporarily in CI",
)


def test_get_my_requests_success(client, users, auth_as, valid_request_payload):
    """User fetches all their requests without status filter"""
    owner = users["user1"]
    auth_as(owner)

    # Create two requests
    payload1 = valid_request_payload(title="Request 1", status=Status.DRAFT)
    payload2 = valid_request_payload(title="Request 2", status=Status.DRAFT)

    resp1 = client.post(f"{API_PREFIX}", json=payload1)
    resp2 = client.post(f"{API_PREFIX}", json=payload2)

    # Assert creation returns 201
    assert resp1.status_code == 201
    assert resp2.status_code == 201

    id1 = resp1.json()["id"]
    id2 = resp2.json()["id"]

    # Confirm requests exist for owner
    response = client.get(f"{API_PREFIX}/my-requests")
    assert response.status_code == 200
    titles = [r["title"] for r in response.json()]
    ids = [r["id"] for r in response.json()]
    assert id1 in ids
    assert id2 in ids
    assert "Request 1" in titles
    assert "Request 2" in titles


def test_get_my_requests_single_status(client, users, auth_as, valid_request_payload):
    """User fetches requests filtered by a single status"""
    owner = users["user1"]
    auth_as(owner)

    payload = valid_request_payload(title="Draft Request", status=Status.DRAFT)
    resp = client.post(f"{API_PREFIX}", json=payload)
    assert resp.status_code == 201
    request_id = resp.json()["id"]

    # Fetch only DRAFT requests
    response = client.get(f"{API_PREFIX}/my-requests?statuses=draft")
    assert response.status_code == 200
    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == request_id
    assert body[0]["status"] == Status.DRAFT


def test_get_my_requests_multiple_statuses(
    client, users, auth_as, seeded_requests_for_user
):
    auth_as(users["user1"])

    response = client.get(f"{API_PREFIX}/my-requests?statuses=draft&statuses=submitted")

    assert response.status_code == 200

    titles = [r["title"] for r in response.json()]

    assert "Draft Req" in titles
    assert "Submitted Req" in titles
    assert "Approved Req" not in titles


def test_get_my_requests_empty_result(client, users, auth_as):
    """User fetches requests with a status that has no matches"""
    owner = users["user1"]
    auth_as(owner)

    # No requests created yet, fetch SUBMITTED
    response = client.get(f"{API_PREFIX}/my-requests?statuses=submitted")
    assert response.status_code == 200
    assert response.json() == []


def test_get_my_requests_user_isolation(client, users, auth_as, valid_request_payload):
    """User cannot see requests of another user"""
    owner = users["user1"]
    other_user = users["user2"]
    auth_as(owner)

    # Owner creates request
    payload = valid_request_payload(title="Private Request", status=Status.DRAFT)
    resp = client.post(f"{API_PREFIX}", json=payload)
    assert resp.status_code == 201
    request_id = resp.json()["id"]

    # Confirm request exists for owner
    response_owner = client.get(f"{API_PREFIX}/my-requests")
    titles_owner = [r["title"] for r in response_owner.json()]
    assert "Private Request" in titles_owner

    # Switch to other user
    auth_as(other_user)
    response_other = client.get(f"{API_PREFIX}/my-requests")
    titles_other = [r["title"] for r in response_other.json()]
    assert "Private Request" not in titles_other
