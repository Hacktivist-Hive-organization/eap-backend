from app.core.config import settings

API_PREFIX = f"{settings.API_V1_PREFIX}/subtypes"


def test_get_all_subtypes(client, seeded_request_types):

    response = client.get(f"{API_PREFIX}")

    assert response.status_code == 200
    assert len(response.json()) >= 1
