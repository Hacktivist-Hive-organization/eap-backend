# tests/integration/requests/test_process_request_admin.py

from fastapi.testclient import TestClient

from app.common.enums import Status


def _get_approved_request(requests):
    return next(r for r in requests if r.current_status == Status.APPROVED)


def _get_admin(dashboard_admin):
    return list(dashboard_admin.values())[0]


def test_admin_can_assign_in_progress_request(
    client: TestClient, seeded_requests_for_user, dashboard_admin, auth_as
):
    request = _get_approved_request(seeded_requests_for_user)
    admin = _get_admin(dashboard_admin)
    auth_as(admin)

    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.IN_PROGRESS.value},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == Status.IN_PROGRESS.value
    assert data["assignee_id"] == admin.id


def test_admin_cannot_assign_in_progress_if_already_assigned(
    client: TestClient, seeded_requests_for_user, dashboard_admin, auth_as
):
    request = _get_approved_request(seeded_requests_for_user)
    admin1 = _get_admin(dashboard_admin)
    admin2 = list(dashboard_admin.values())[1]

    # First admin assigns
    auth_as(admin1)
    client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.IN_PROGRESS.value},
    )

    # Second admin tries to assign
    auth_as(admin2)
    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.IN_PROGRESS.value},
    )

    assert response.status_code == 400
    assert "another admin already working" in response.json()["detail"].lower()


def test_admin_can_complete_in_progress_request(
    client: TestClient, seeded_requests_for_user, dashboard_admin, auth_as
):
    request = _get_approved_request(seeded_requests_for_user)
    admin = _get_admin(dashboard_admin)
    auth_as(admin)

    # Assign first
    client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.IN_PROGRESS.value},
    )

    # Complete
    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.COMPLETED.value},
    )
    assert response.status_code == 200
    assert response.json()["current_status"] == Status.COMPLETED.value


def test_admin_can_reject_in_progress_request_with_comment(
    client: TestClient, seeded_requests_for_user, dashboard_admin, auth_as
):
    request = _get_approved_request(seeded_requests_for_user)
    admin = _get_admin(dashboard_admin)
    auth_as(admin)

    # Assign first
    client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.IN_PROGRESS.value},
    )

    # Reject with comment
    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.REJECTED.value, "comment": "Reject reason"},
    )
    assert response.status_code == 200
    assert response.json()["current_status"] == Status.REJECTED.value
