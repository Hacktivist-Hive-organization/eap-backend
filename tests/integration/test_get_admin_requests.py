# tests/integration/test_get_admin_requests.py

from app.core.config import settings

API_PREFIX = f"{settings.API_V1_PREFIX}"


def test_get_all_requests_except_draft(
    client, dashboard_admin, auth_as, users, seeded_requests_for_user
):
    admin = dashboard_admin["admin1"]
    auth_as(admin)

    response = client.get(f"{API_PREFIX}/requests")
    assert response.status_code == 200
    titles = [r["title"] for r in response.json()]
    assert "Draft Req" not in titles
    assert "Submitted Req" in titles
    assert "Approved Req" in titles
    assert "Rejected Req" in titles


def test_admin_permission(client, auth_as, users, seeded_requests_for_user):
    user1 = users["user1"]
    auth_as(user1)

    response = client.get(f"{API_PREFIX}/requests")
    assert response.status_code == 403


def test_get_approved_requests(
    client, dashboard_admin, auth_as, users, seeded_requests_for_user
):
    admin = dashboard_admin["admin1"]
    auth_as(admin)

    response = client.get(f"{API_PREFIX}/requests?status=approved")
    assert response.status_code == 200
    titles = [r["title"] for r in response.json()]
    assert "Draft Req" not in titles
    assert "Submitted Req" not in titles
    assert "Approved Req" in titles
    assert "Rejected Req" not in titles
