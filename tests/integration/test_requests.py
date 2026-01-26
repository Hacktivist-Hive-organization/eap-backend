from tests.integration.helpers import seed_types_and_subtypes
from app.common.enums import Status, Priority


def test_create_draft_request_success(client, db_session):

    data = seed_types_and_subtypes(db_session)

    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Fix laptop",
        "description": "Laptop does not start properly and needs repair.",
        "business_justification": "Employee cannot work without laptop.",
        "priority": "high"
    }

    response = client.post("/api/v1/requests", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == Status.DRAFT
    assert body["type"]["name"] == "Hardware"
    assert body["subtype"]["name"] == "Laptop"
    assert body["updated_at"] is None


def test_create_request_type_not_found(client, db_session):
    payload = {
        "type_id": 999,
        "subtype_id": 1,
        "title": "Fix printer",
        "description": "Printer broken and cannot print documents.",
        "business_justification": "Office cannot operate without printer.",
        "priority": "low"
    }

    response = client.post("/api/v1/requests", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Request type not found: no type exists with id 999"
    }


def test_create_request_subtype_mismatch(client, db_session):

    data = seed_types_and_subtypes(db_session)

    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["license"].id,  # belongs to software
        "title": "Wrong subtype",
        "description": "Testing wrong subtype validation.",
        "business_justification": "Testing business rules.",
        "priority": "medium"
    }

    response = client.post("/api/v1/requests", json=payload)

    assert response.status_code == 400
    assert "subtype mismatch" in response.json()["detail"]


def test_create_request_invalid_priority(client, db_session):
    """Test that invalid priority values are rejected by Pydantic validation"""
    data = seed_types_and_subtypes(db_session)

    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Fix laptop",
        "description": "Laptop does not start properly and needs repair.",
        "business_justification": "Employee cannot work without laptop.",
        "priority": "URGENT"  # Invalid
    }

    response = client.post("/api/v1/requests", json=payload)

    assert response.status_code == 400
    assert "priority: Input should be 'low', 'medium' or 'high'" in response.json()["detail"]

def test_create_request_status_defaults_to_draft(client, db_session):
    """Test that status is defaulted to Draft if not provided"""
    data = seed_types_and_subtypes(db_session)

    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Install Zoom",
        "description": "Need Zoom installed on new laptop for remote meetings.",
        "business_justification": "Required for remote collaboration.",
        "priority": "medium"  # Lowercase should still work because enum is string
    }

    response = client.post("/api/v1/requests", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == Status.DRAFT
    assert body["priority"] == Priority.MEDIUM

def test_create_request_status_always_draft(client, db_session):
    """Test that status is always Draft on create, even if FE sends another value"""
    data = seed_types_and_subtypes(db_session)

    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Install Zoom",
        "description": "Need Zoom installed on new laptop for remote meetings.",
        "business_justification": "Required for remote collaboration.",
        "priority": "high",
        "status": "submitted"  # FE tries to override
    }

    response = client.post("/api/v1/requests", json=payload)
    body = response.json()

    assert response.status_code == 200
    # Status is always Draft
    assert body["status"] == Status.DRAFT
    # Priority is accepted correctly
    assert body["priority"] == Priority.HIGH



def test_create_request_validation_error(client):
    payload = {
        "type_id": 1,
        "subtype_id": 1,
        "title": "Fix laptop",
        "description": "Too short",
        "business_justification": "Too short",
        "priority": "low"
    }

    response = client.post("/api/v1/requests", json=payload)

    assert response.status_code == 400
    assert "description: String should have at least 20 characters" in response.json()["detail"]


def test_create_request_letters_validation(client, db_session):
    """Ensure title, description, and business_justification include at least one letter"""
    # Seed types/subtypes
    from tests.integration.helpers import seed_types_and_subtypes
    data = seed_types_and_subtypes(db_session)

    # Payload with numbers only (invalid)
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Fix laptop",
        "description": "Need Zoom installed on new laptop for remote meetings.",
        "business_justification": "00011122222222222222222222222222222",
        "priority": "high"
    }

    response = client.post("/api/v1/requests", json=payload)
    assert response.status_code == 400

    body = response.json()

    assert ("business_justification: Value error, business_justification "
            "must contain at least one letter"
            in response.json()[
        "detail"])
