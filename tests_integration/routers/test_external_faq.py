from typing import Any

from assertpy import assert_that
from fastapi.testclient import TestClient

from httpx import Response
from pytest_httpserver import HTTPServer
from werkzeug import Request

EXTERNAL_FAQ_ENDPOINT = "/context/external-faq"


def test_external_faq_get(
    mock_external_faq_server: HTTPServer,
    test_client: TestClient,
):
    external_faq: list[dict[str, Any]] = [
        {"name": "faq-1", "tag": "product", "id": 2},
        {"name": "faq-2", "tag": "product", "id": 3},
    ]
    mock_external_faq_server.expect_request("/faqs", method="GET").respond_with_json(
        external_faq
    )

    get_response: Response = test_client.get(EXTERNAL_FAQ_ENDPOINT)
    assert_that(get_response.status_code).is_equal_to(200)
    assert_that(get_response.json()).is_equal_to(external_faq)

    requests_made: list[Request] = [req for req, res in mock_external_faq_server.log]
    assert_that(requests_made).is_length(1)
    assert_that(requests_made[0].path).is_equal_to("/faqs")
    assert_that(requests_made[0].method).is_equal_to("GET")
