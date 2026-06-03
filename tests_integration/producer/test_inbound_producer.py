import uuid
from datetime import datetime, UTC, timedelta
from datetime import timezone
from decimal import Decimal
from typing import MutableMapping, Any

from aio_pika.abc import HeadersType
from assertpy import assert_that
from deepdiff import DeepDiff
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from httpx import Response
from tenacity import Retrying, stop_after_delay, wait_fixed

from app.config import Settings
from app.model.response.sample import Sample

PUBLISH_INBOUND_ENDPOINT = "/context/test-support/publish-inbound-messages"
PUBLISH_BULK_INBOUND_ENDPOINT = "/context/test-support/publish-bulk-inbound-messages"


def test_publish_inbound_message(
    enable_test_routers: Settings,
    test_client: TestClient,
    captured_logs: list[MutableMapping[str, Any]],
):
    sample1: Sample = Sample(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.0,
        decimal_field=Decimal("3.1"),
        created_datetime=datetime.now(timezone.utc),
        updated_datetime=datetime.now(timezone.utc),
        version=1,
    )
    sample2: Sample = Sample(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=None,
        float_field=None,
        decimal_field=None,
        created_datetime=datetime.now(timezone.utc),
        updated_datetime=datetime.now(timezone.utc),
        version=1,
    )
    message: list[Sample] = [sample1, sample2]
    publish_response: Response = test_client.post(
        PUBLISH_INBOUND_ENDPOINT, json=jsonable_encoder(message)
    )
    assert_that(publish_response.status_code).is_equal_to(204)

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
            assert_that(inbound_consumer_logs).is_length(1)
            headers: HeadersType = inbound_consumer_logs[0]["headers"]
            assert_that(headers.get("test")).is_equal_to("value")
            assert_that(headers.get("datetime")).is_instance_of(datetime)
            assert_that(headers.get("datetime")).is_between(
                datetime.now(UTC) - timedelta(seconds=5),
                datetime.now(UTC) + timedelta(seconds=5),
            )
            consumed_samples: list[dict[str, Any]] = inbound_consumer_logs[0]["samples"]
            assert_that(
                DeepDiff(
                    consumed_samples,
                    jsonable_encoder(message),
                    ignore_order=True,
                )
            ).is_empty()


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
