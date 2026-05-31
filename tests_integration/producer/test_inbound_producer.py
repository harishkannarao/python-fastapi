from typing import MutableMapping, Any

from assertpy import assert_that
from fastapi.testclient import TestClient

from httpx import Response
from tenacity import Retrying, stop_after_delay, wait_fixed

from app.config import Settings

PUBLISH_BULK_INBOUND_ENDPOINT = "/context/test-support/publish-bulk-inbound-messages"


def test_publish_bulk_inbound_message(
    enable_test_routers: Settings,
    test_client: TestClient,
    captured_logs: list[MutableMapping[str, Any]],
):
    count: int = 2
    publish_bulk_response: Response = test_client.get(
        f"{PUBLISH_BULK_INBOUND_ENDPOINT}?count={count}"
    )
    assert_that(publish_bulk_response.status_code).is_equal_to(204)

    for attempt in Retrying(
        stop=stop_after_delay(5), wait=wait_fixed(0.5), reraise=True
    ):
        with attempt:
            assert_that(len(captured_logs)).is_greater_than(0)
            inbound_consumer_logs = list(
                filter(
                    lambda entry: str(entry["event"]).startswith(
                        "Processed inbound message"
                    ),
                    captured_logs,
                )
            )
            assert_that(inbound_consumer_logs).is_length(count)
