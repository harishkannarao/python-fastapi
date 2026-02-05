import uuid
from typing import MutableMapping, Any

from fastapi.testclient import TestClient


def test_new_request_id_when_not_supplied_in_request(
    test_client: TestClient,
    captured_logs: list[MutableMapping[str, Any]],
):
    response = test_client.get("")

    assert response.status_code == 200
    assert response.headers.get("x-request-id") is not None
    request_id = response.headers.get("x-request-id")
    assert len(captured_logs) > 0
    filtered_logs = list(
        filter(lambda entry: entry["event"] == "Request finished", captured_logs)
    )
    assert len(filtered_logs) >= 1
    assert filtered_logs[0]["request_id"] == request_id


def test_returns_request_id_when_supplied_in_request(
    test_client: TestClient,
    captured_logs: list[MutableMapping[str, Any]],
):
    request_id = str(uuid.uuid4())
    response = test_client.get("", headers={"x-request-id": request_id})
    assert response.status_code == 200
    assert response.headers.get("x-request-id") == request_id
    assert len(captured_logs) > 0
    filtered_logs = list(
        filter(lambda entry: entry["event"] == "Request finished", captured_logs)
    )
    assert len(filtered_logs) >= 1
    assert filtered_logs[0]["request_id"] == request_id
