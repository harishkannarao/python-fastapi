from assertpy import assert_that
from fastapi.testclient import TestClient

from httpx import Response
from pytest_httpserver import HTTPServer

EXTERNAL_FAQ_ENDPOINT = "/context/external-faq"


def test_external_faq_get(
    mock_external_faq_server: HTTPServer,
    test_client: TestClient,
):
    external_faq = [
        {"name": "faq-1", "tag": "product", "id": 2},
        {"name": "faq-2", "tag": "product", "id": 3},
    ]
    mock_external_faq_server.expect_request("/faqs", method="GET").respond_with_json(
        external_faq
    )

    get_response: Response = test_client.get(EXTERNAL_FAQ_ENDPOINT)
    assert_that(get_response.status_code).is_equal_to(200)
    assert_that(get_response.json()).is_equal_to(external_faq)
