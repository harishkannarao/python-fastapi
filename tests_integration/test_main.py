from fastapi.testclient import TestClient

from app.config import Settings


def test_root_get(test_client: TestClient):
    response = test_client.get("")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Bigger Applications!"}
    assert response.headers.get("x-process-time") is not None


def test_root_swagger_and_open_api(test_client: TestClient):
    swagger_response = test_client.get("/docs")
    assert swagger_response.status_code == 200

    open_api_response = test_client.get("/openapi.json")
    assert open_api_response.status_code == 200


def test_root_swagger_and_open_api_disabled(
    disable_open_api: Settings,
    test_client: TestClient,
):
    assert disable_open_api.app_open_api_url == ""

    swagger_response = test_client.get("/docs")
    assert swagger_response.status_code == 404

    open_api_response = test_client.get("/openapi.json")
    assert open_api_response.status_code == 404


def test_context_root_get(test_client: TestClient):
    response = test_client.get("/context")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Sub Application!"}
    assert response.headers.get("x-process-time") is not None


def test_context_swagger_and_open_api(test_client: TestClient):
    swagger_response = test_client.get("/context/docs")
    assert swagger_response.status_code == 200

    open_api_response = test_client.get("/context/openapi.json")
    assert open_api_response.status_code == 200


def test_context_root_swagger_and_open_api_disabled(
    disable_open_api: Settings,
    test_client: TestClient,
):
    assert disable_open_api.app_open_api_url == ""

    swagger_response = test_client.get("/context/docs")
    assert swagger_response.status_code == 404

    open_api_response = test_client.get("/context/openapi.json")
    assert open_api_response.status_code == 404
