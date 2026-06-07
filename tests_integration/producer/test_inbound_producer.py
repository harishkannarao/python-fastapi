import json
import uuid
from datetime import datetime, UTC, timedelta
from decimal import Decimal
from typing import MutableMapping, Any
from unittest.mock import AsyncMock

import pytest
from aio_pika.abc import HeadersType
from assertpy import assert_that
from deepdiff import DeepDiff
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from httpx import Response
from pytest_mock import MockerFixture
from tenacity import Retrying, stop_after_delay, wait_fixed

from app.config import Settings
from app.model.response.sample import Sample
from tests_integration.support.model.inbound_message import InboundMessage

PUBLISH_INBOUND_ENDPOINT = "/context/test-support/publish-inbound-messages"
PUBLISH_BULK_INBOUND_ENDPOINT = "/context/test-support/publish-bulk-inbound-messages"


@pytest.fixture
def mock_publish_to_outbound(mocker: MockerFixture) -> AsyncMock:
    mock: AsyncMock = mocker.patch("app.consumer.inbound_consumer.publish_to_outbound")
    return mock


def test_publish_inbound_message(
    enable_test_components: Settings,
    test_client: TestClient,
    captured_logs: list[MutableMapping[str, Any]],
):
    sample1: Sample = Sample(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.0,
        decimal_field=Decimal("3.1"),
        created_datetime=datetime.now(UTC),
        updated_datetime=datetime.now(UTC),
        version=1,
    )
    sample2: Sample = Sample(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=None,
        float_field=None,
        decimal_field=None,
        created_datetime=datetime.now(UTC),
        updated_datetime=datetime.now(UTC),
        version=1,
    )
    samples: list[Sample] = [sample1, sample2]
    headers: dict[str, Any] = {
        "test": "value",
        "int_value": 2,
        "datetime": datetime.now(UTC).isoformat(),
    }
    message: InboundMessage = InboundMessage(samples=samples, headers=headers)
    publish_response: Response = test_client.post(
        PUBLISH_INBOUND_ENDPOINT, json=jsonable_encoder(message)
    )
    assert_that(publish_response.status_code).is_equal_to(204)

    for attempt in Retrying(
        stop=stop_after_delay(5), wait=wait_fixed(0.5), reraise=True
    ):
        with attempt:
            assert_that(len(captured_logs)).is_greater_than(0)
            outbound_consumer_logs = list(
                filter(
                    lambda entry: str(entry["event"]).startswith(
                        "Processed outbound message"
                    ),
                    captured_logs,
                )
            )
            assert_that(outbound_consumer_logs).is_length(1)
            outbound_headers: HeadersType = outbound_consumer_logs[0]["headers"]
            assert_that(outbound_headers.get("test")).is_equal_to(headers.get("test"))
            assert_that(outbound_headers.get("int_value")).is_equal_to(
                headers.get("int_value")
            )
            assert_that(
                datetime.fromisoformat(outbound_headers.get("datetime"))
            ).is_between(
                datetime.now(UTC) - timedelta(seconds=5),
                datetime.now(UTC) + timedelta(seconds=5),
            )
            outbound_samples: list[dict[str, Any]] = outbound_consumer_logs[0][
                "samples"
            ]
            assert_that(
                DeepDiff(
                    outbound_samples,
                    jsonable_encoder(samples),
                    ignore_order=True,
                )
            ).is_empty()


def test_publish_inbound_message_publishes_to_retries_and_succeeds_on_last_attempt(
    enable_test_components: Settings,
    mock_publish_to_outbound: AsyncMock,
    test_client: TestClient,
    captured_logs: list[MutableMapping[str, Any]],
):
    async def publish_outbound_side_effect_logic(*args, **kwargs):
        if mock_publish_to_outbound.call_count == 1:
            raise ValueError("First failure")
        if mock_publish_to_outbound.call_count == 2:
            raise TypeError("Second failure")
        # Call 3 and all future calls fall back to returning None
        return None

    mock_publish_to_outbound.side_effect = publish_outbound_side_effect_logic

    sample1: Sample = Sample(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.0,
        decimal_field=Decimal("3.1"),
        created_datetime=datetime.now(UTC),
        updated_datetime=datetime.now(UTC),
        version=1,
    )
    samples: list[Sample] = [sample1]
    headers: dict[str, Any] = {
        "test": "value",
        "int_value": 2,
        "datetime": datetime.now(UTC).isoformat(),
        "message_id": str(uuid.uuid4()),
    }
    message: InboundMessage = InboundMessage(samples=samples, headers=headers)
    publish_response: Response = test_client.post(
        PUBLISH_INBOUND_ENDPOINT, json=jsonable_encoder(message)
    )
    assert_that(publish_response.status_code).is_equal_to(204)

    for attempt in Retrying(
        stop=stop_after_delay(15), wait=wait_fixed(0.5), reraise=True
    ):
        with attempt:
            assert_that(len(captured_logs)).is_greater_than(0)
            retry_sent_to_inbound_logs = list(
                filter(
                    lambda entry: str(entry["event"]).startswith(
                        "Sent to inbound queue"
                    ),
                    captured_logs,
                )
            )
            assert_that(retry_sent_to_inbound_logs).is_length(2)
            retry_headers: HeadersType = retry_sent_to_inbound_logs[0]["headers"]
            assert_that(retry_headers.get("test")).is_equal_to(headers.get("test"))
            assert_that(retry_headers.get("message_id")).is_equal_to(
                headers.get("message_id")
            )
            assert_that(retry_headers.get("int_value")).is_equal_to(
                headers.get("int_value")
            )
            assert_that(
                datetime.fromisoformat(retry_headers.get("datetime"))
            ).is_between(
                datetime.now(UTC) - timedelta(seconds=10),
                datetime.now(UTC) + timedelta(seconds=10),
            )
            retry_payload_string = retry_sent_to_inbound_logs[0]["payload_string"]
            outbound_samples: list[dict[str, Any]] = json.loads(retry_payload_string)
            assert_that(
                DeepDiff(
                    outbound_samples,
                    jsonable_encoder(samples),
                    ignore_order=True,
                )
            ).is_empty()

    retry_sent_to_retry_logs = list(
        filter(
            lambda entry: str(entry["event"]).startswith("Sent to retry queue"),
            captured_logs,
        )
    )
    assert_that(len(retry_sent_to_retry_logs)).is_greater_than(1)

    for attempt in Retrying(
        stop=stop_after_delay(5), wait=wait_fixed(0.5), reraise=True
    ):
        with attempt:
            assert_that(mock_publish_to_outbound.call_count).is_equal_to(3)

    assert_that(
        mock_publish_to_outbound.call_args_list[2].kwargs["samples"]
    ).is_equal_to(samples)

def test_publish_inbound_message_exhausts_after_max_retries(
    enable_test_components: Settings,
    mock_publish_to_outbound: AsyncMock,
    test_client: TestClient,
    captured_logs: list[MutableMapping[str, Any]],
):
    mock_publish_to_outbound.side_effect = ValueError("Dummy failure")

    sample1: Sample = Sample(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.0,
        decimal_field=Decimal("3.1"),
        created_datetime=datetime.now(UTC),
        updated_datetime=datetime.now(UTC),
        version=1,
    )
    samples: list[Sample] = [sample1]
    headers: dict[str, Any] = {
        "message_id": str(uuid.uuid4()),
    }
    message: InboundMessage = InboundMessage(samples=samples, headers=headers)
    publish_response: Response = test_client.post(
        PUBLISH_INBOUND_ENDPOINT, json=jsonable_encoder(message)
    )
    assert_that(publish_response.status_code).is_equal_to(204)

    for attempt in Retrying(
        stop=stop_after_delay(15), wait=wait_fixed(0.5), reraise=True
    ):
        with attempt:
            assert_that(len(captured_logs)).is_greater_than(0)
            retry_sent_to_inbound_logs = list(
                filter(
                    lambda entry: str(entry["event"]).startswith(
                        "Sent to inbound queue"
                    ),
                    captured_logs,
                )
            )
            assert_that(retry_sent_to_inbound_logs).is_length(2)
            retry_exhausted_logs = list(
                filter(
                    lambda entry: str(entry["event"]).startswith(
                        "Max retries exhausted, discarding message"
                    ),
                    captured_logs,
                )
            )
            assert_that(retry_exhausted_logs).is_length(1)

    for attempt in Retrying(
        stop=stop_after_delay(5), wait=wait_fixed(0.5), reraise=True
    ):
        with attempt:
            assert_that(mock_publish_to_outbound.call_count).is_equal_to(3)



def test_publish_bulk_inbound_message(
    enable_test_components: Settings,
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
