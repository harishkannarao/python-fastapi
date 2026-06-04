from typing import MutableMapping, Any

from assertpy import assert_that
from fastapi.testclient import TestClient

from httpx import Response

from app.config import Settings

ENDPOINT = "/context/test-support/get"


def test_support_get_returns_success_when_enabled(
    enable_test_components: Settings,
    test_client: TestClient,
    captured_logs: list[MutableMapping[str, Any]],
):
    get_response: Response = test_client.get(ENDPOINT)
    assert_that(get_response.status_code).is_equal_to(200)
    assert_that(get_response.json()["value"]).is_equal_to("test-value")

    assert_that(len(captured_logs)).is_greater_than(0)
    expected_logs = list(
        filter(
            lambda entry: str(entry["event"]).startswith("Support Request Success!"),
            captured_logs,
        )
    )
    assert_that(expected_logs).is_length(1)
    assert_that(expected_logs[0]["value"]).is_equal_to("test-value")


def test_support_get_returns_404_as_default(
    disable_test_components: Settings,
    test_client: TestClient,
):
    get_response: Response = test_client.get(ENDPOINT)
    assert_that(get_response.status_code).is_equal_to(404)
