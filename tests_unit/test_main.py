from fastapi.testclient import TestClient


def test_root_get(test_client: TestClient):
    response = test_client.get("")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Bigger Applications!"}


def test_context_root_get(test_client: TestClient):
    response = test_client.get("/context")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Sub Application!"}
