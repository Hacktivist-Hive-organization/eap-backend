from tests.integration.helpers import seed_types_and_subtypes


def test_get_all_subtypes(client, db_session):

    seed_types_and_subtypes(db_session)

    response = client.get("/api/v1/subtypes")

    assert response.status_code == 200
    assert len(response.json()) >= 1

