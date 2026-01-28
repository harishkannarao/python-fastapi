from assertpy import assert_that
from fastapi.testclient import TestClient

from httpx import Response

EXTERNAL_FAQ_ENDPOINT = "/context/external-faq"


def test_external_faq_get(
    test_client: TestClient,
):
    get_response: Response = test_client.get(EXTERNAL_FAQ_ENDPOINT)
    assert_that(get_response.status_code).is_equal_to(200)
