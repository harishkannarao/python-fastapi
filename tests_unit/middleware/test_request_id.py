import uuid

from fastapi.testclient import TestClient


def test_new_request_id_when_not_supplied_in_request(test_client: TestClient):
    response = test_client.get("")
    assert response.status_code == 200
    assert response.headers.get("x-request-id") is not None


def test_returns_request_id_when_supplied_in_request(test_client: TestClient):
    request_id = str(uuid.uuid4())
    response = test_client.get("", headers={"x-request-id": request_id})
    assert response.status_code == 200
    assert response.headers.get("x-request-id") == request_id
