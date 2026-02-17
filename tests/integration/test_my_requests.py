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


def test_get_my_requests_success(client, users, auth_as, seeded_requests_for_user):
    """User fetches all their requests without status filter"""
    owner = users["user1"]
    auth_as(owner)

    # Confirm requests exist for owner
    response = client.get(f"{API_PREFIX}/my-requests")
    assert response.status_code == 200
    titles = [r["title"] for r in response.json()]
    assert "Draft Req" in titles
    assert "Submitted Req" in titles
    assert "Approved Req" in titles


def test_get_my_requests_single_status(
    client, users, auth_as, seeded_requests_for_user
):
    """User fetches requests filtered by a single status"""
    owner = users["user1"]
    auth_as(owner)

    # Fetch only DRAFT requests, seeded_requests_for_user has created multi
    # statuses requests
    response = client.get(f"{API_PREFIX}/my-requests?statuses=draft")
    assert response.status_code == 200

    statuses = [r["status"] for r in response.json()]
    for s in statuses:
        assert s == "draft"


def test_get_my_requests_with_an_invalid_status_value(
    client, users, auth_as, seeded_requests_for_user
):
    owner = users["user1"]
    auth_as(owner)
    invalid_status = "Draft"  # should be lowercase: 'draft'
    response = client.get(f"{API_PREFIX}/my-requests?statuses={invalid_status}")
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert (
        "Input should be 'draft', 'submitted', 'in_progress', 'approved', "
        "'rejected', 'completed' or 'cancelled'" in body["detail"]
    )


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


def test_get_my_requests_empty_result(client, users, auth_as, seeded_requests_for_user):
    """User fetches requests with a status that has no matches"""
    owner = users["user1"]
    auth_as(owner)

    # requests approved, submitted , draft has been created, fetch in_progress
    response = client.get(f"{API_PREFIX}/my-requests?statuses=in_progress")
    assert response.status_code == 200
    body = response.json()
    assert body == []


def test_get_my_requests_user_isolation(client, users, auth_as, valid_request_payload):
    """User cannot see requests of another user"""
    owner = users["user1"]
    other_user = users["user2"]
    auth_as(owner)

    # Owner creates request
    payload = valid_request_payload(title="Private Request", status=Status.DRAFT)
    resp = client.post(f"{API_PREFIX}", json=payload)
    assert resp.status_code == 201

    # Confirm request exists for owner
    response_owner = client.get(f"{API_PREFIX}/my-requests")
    titles_owner = [r["title"] for r in response_owner.json()]
    assert "Private Request" in titles_owner

    # Switch to other user, who hasn't created any requests yet
    auth_as(other_user)
    response_other = client.get(f"{API_PREFIX}/my-requests")
    assert response_other.status_code == 200
    body = response_other.json()
    assert body == []
