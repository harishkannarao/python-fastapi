from fastapi.testclient import TestClient
from assertpy import assert_that


def test_get_users(test_client: TestClient):
    response = test_client.get("/context/users")
    assert response.status_code == 200
    result = response.json()
    assert_that(result).contains({"username": "Morty"})
    assert_that(result).contains({"username": "Rick"})
    assert_that(result).is_length(2)
