# tests/integration/test_requests.py

import os

import pytest

from app.common.enums import Priority, Status
from app.core.config import settings

API_PREFIX = f"{settings.API_V1_PREFIX}/requests"

# Skip only with CI
pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="DbUser.username not ready, skipping temporarily in CI",
)


def test_create_draft_request_success(client, seeded_request_types, users, auth_as):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Fix laptop",
        "description": "Laptop does not start properly and needs repair.",
        "business_justification": "Employee cannot work without laptop.",
        "priority": "high",
    }

    response = client.post(f"{API_PREFIX}", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["current_status"] == Status.DRAFT
    assert body["type"]["name"] == "Hardware"
    assert body["subtype"]["name"] == "Laptop"
    assert body["updated_at"] is not None


def test_create_request_type_not_found(client, seeded_request_types, users, auth_as):
    owner = users["user1"]
    auth_as(owner)

    payload = {
        "type_id": 999,
        "subtype_id": 1,
        "title": "Fix printer",
        "description": "Printer broken and cannot print documents.",
        "business_justification": "Office cannot operate without printer.",
        "priority": "low",
        "requester_id": 1,
    }

    response = client.post(f"{API_PREFIX}", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Request type not found: no type exists with id 999"
    }


def test_create_request_subtype_mismatch(client, seeded_request_types, users, auth_as):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)

    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["license"].id,  # belongs to software
        "title": "Wrong subtype",
        "description": "Testing wrong subtype validation.",
        "business_justification": "Testing business rules.",
        "priority": "medium",
        "requester_id": users["user1"].id,
    }

    response = client.post(f"{API_PREFIX}", json=payload)

    assert response.status_code == 400
    assert "subtype mismatch" in response.json()["detail"]


def test_create_request_invalid_priority(client, seeded_request_types, users, auth_as):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)

    """Test that invalid priority values are rejected by Pydantic validation"""
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Fix laptop",
        "description": "Laptop does not start properly and needs repair.",
        "business_justification": "Employee cannot work without laptop.",
        "priority": "URGENT",  # Invalid
    }

    response = client.post(f"{API_PREFIX}", json=payload)

    assert response.status_code == 422
    assert (
        "priority: Input should be 'low', 'medium' or 'high'"
        in response.json()["detail"]
    )


def test_create_request_status_defaults_to_draft(
    client, seeded_request_types, users, auth_as
):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)

    """Test that status is defaulted to Draft if not provided"""
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Install Zoom",
        "description": "Need Zoom installed on new laptop for remote meetings.",
        "business_justification": "Required for remote collaboration.",
        "priority": "medium",
        "requester_id": users["user1"].id,
    }

    response = client.post(f"{API_PREFIX}", json=payload)
    body = response.json()

    assert response.status_code == 201
    assert body["current_status"] == Status.DRAFT
    assert body["priority"] == Priority.MEDIUM


def test_create_request_status_always_draft(
    client, seeded_request_types, users, auth_as
):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)

    """Test that status is always Draft on create, even if FE sends another value"""
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Install Zoom",
        "description": "Need Zoom installed on new laptop for remote meetings.",
        "business_justification": "Required for remote collaboration.",
        "priority": "high",
        "current_status": "submitted",  # FE tries to override
        "requester_id": users["user1"].id,
    }

    response = client.post("/api/v1/requests", json=payload)
    body = response.json()

    assert response.status_code == 201
    # Status is always Draft
    assert body["current_status"] == Status.DRAFT
    # Priority is accepted correctly
    assert body["priority"] == Priority.HIGH


def test_create_request_validation_error(client, seeded_request_types, users, auth_as):
    owner = users["user1"]
    auth_as(owner)

    payload = {
        "type_id": 1,
        "subtype_id": 1,
        "title": "Fix laptop",
        "description": "Too short",
        "business_justification": "Too short",
        "priority": "low",
        "requester_id": 1,
    }

    response = client.post(f"{API_PREFIX}", json=payload)

    assert response.status_code == 422
    assert (
        "description: String should have at least 20 characters"
        in response.json()["detail"]
    )


def test_create_request_letters_validation(
    client, seeded_request_types, users, auth_as
):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)

    """Ensure title, description, and business_justification include at least one letter"""
    # Payload with numbers only (invalid)
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Fix laptop",
        "description": "Need Zoom installed on new laptop for remote meetings.",
        "business_justification": "00011122222222222222222222222222222",
        "priority": "high",
        "requester_id": users["user1"].id,
    }

    response = client.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == 422

    body = response.json()

    assert (
        "business_justification: Value error, business_justification "
        "must contain at least one letter" in response.json()["detail"]
    )
