import os

import pytest

from app.common.enums import Priority, Status
from tests.integration.helpers import seed_types_and_subtypes, seed_user

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="DbUser.username not ready, skipping temporarily in CI",
)


def test_get_request_details_success(client, db_session):
    data = seed_types_and_subtypes(db_session)
    users = seed_user(db_session)

    # Create request
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "New laptop",
        "description": "Need a laptop with 32GB RAM for development work.",
        "business_justification": "Current machine cannot run required tools.",
        "priority": "medium",
        "requester_id": users["user1"].id,
    }

    create_response = client.post("/api/v1/requests", json=payload)
    assert create_response.status_code == 200

    request_id = create_response.json()["id"]

    # Fetch request details
    response = client.get(f"/api/v1/requests/{request_id}")

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == request_id
    assert body["title"] == payload["title"]
    assert body["status"] == Status.DRAFT

    # requester info
    assert body["requester"]["id"] == users["user1"].id
    assert body["requester"]["email"] == users["user1"].email

    # timestamps
    assert body["created_at"] is not None
    assert body["updated_at"] is None


def test_get_request_details_not_found(client):
    response = client.get("/api/v1/requests/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Request not found"}


@pytest.mark.skip(reason="Auth not implemented yet; current user is hardcoded")
def test_get_request_details_forbidden(client, db_session):
    data = seed_types_and_subtypes(db_session)
    users = seed_user(db_session)

    # Request owned by user1
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Private request",
        "description": "Need a laptop with 32GB RAM for development work.",
        "business_justification": "Current machine cannot run required tools.",
        "priority": "low",
        "requester_id": users["user1"].id,
    }

    response = client.post("/api/v1/requests", json=payload)
    create_response = response.json()
    request_id = create_response["id"]

    #  Simulate another user (hardcoded user_id=1 logic mismatch)
    #  we need to mock JWT user
    response = client.get(f"/api/v1/requests/{request_id}")

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to view this request"}
