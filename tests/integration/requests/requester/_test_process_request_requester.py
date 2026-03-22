# tests/integration/requests/test_process_request_requester.py

import pytest
from fastapi.testclient import TestClient

from app.common.enums import Status


def _get_submitted_request(requests):
    return next(r for r in requests if r.current_status == Status.SUBMITTED)


def _get_cancelled_request(requests):
    return next(r for r in requests if r.current_status == Status.CANCELLED)


def test_requester_can_cancel_submitted_request(
    client: TestClient, seeded_requests_for_user, auth_as
):
    request = _get_submitted_request(seeded_requests_for_user)
    requester = request.requester
    auth_as(requester)

    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.CANCELLED.value},
    )

    assert response.status_code == 200
    assert response.json()["current_status"] == Status.CANCELLED.value


def test_requester_can_reopen_cancelled_request(
    client: TestClient, seeded_requests_for_user, auth_as
):
    request = _get_cancelled_request(seeded_requests_for_user)
    requester = request.requester
    auth_as(requester)

    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.DRAFT.value},
    )

    assert response.status_code == 200
    assert response.json()["current_status"] == Status.DRAFT.value


def test_requester_cannot_approve_request(
    client: TestClient, seeded_requests_for_user, auth_as
):
    request = _get_submitted_request(seeded_requests_for_user)
    requester = request.requester
    auth_as(requester)

    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.APPROVED.value},
    )

    assert response.status_code == 403
    assert "role" in response.json()["detail"].lower()
