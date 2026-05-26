import datetime
import json
import uuid
from decimal import Decimal
from typing import MutableMapping, Any

import aio_pika
import pytest
import structlog
from assertpy import assert_that
from deepdiff import DeepDiff
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from tenacity import Retrying, stop_after_delay, wait_fixed


from app.model.response.sample import Sample


@pytest.mark.asyncio
async def test_inbound_consumer_handles_message_successfully(
    test_client: TestClient,
    captured_logs: list[MutableMapping[str, Any]],
):
    sample1: Sample = Sample(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.0,
        decimal_field=Decimal("3.1"),
        created_datetime=datetime.datetime.now(datetime.UTC),
        updated_datetime=datetime.datetime.now(datetime.UTC),
        version=1,
    )
    sample2: Sample = Sample(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=None,
        float_field=None,
        decimal_field=None,
        created_datetime=datetime.datetime.now(datetime.UTC),
        updated_datetime=datetime.datetime.now(datetime.UTC),
        version=1,
    )
    input_samples: list[Sample] = [sample1, sample2]

    await publish_to_inbound(input_samples)

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
            consumed_samples: list[dict[str, Any]] = inbound_consumer_logs[0]["samples"]
            assert_that(
                DeepDiff(
                    consumed_samples,
                    jsonable_encoder(input_samples),
                    ignore_order=True,
                )
            ).is_empty()


async def publish_to_inbound(samples: list[Sample]):
    logger = structlog.get_logger()
    from app.config import settings

    rabbit_mq_url = (
        f"amqp://{settings.app_rabbit_mq_username}:{settings.app_rabbit_mq_password}"
        f"@{settings.app_rabbit_mq_host}:{settings.app_rabbit_mq_port}/{settings.app_rabbit_mq_vhost}"
    )

    async with await aio_pika.connect_robust(rabbit_mq_url) as connection:
        async with connection.channel() as channel:
            exchange = await channel.get_exchange(settings.app_rabbit_inbound_exchange)
            payload_string: str = json.dumps(jsonable_encoder(samples))
            message = aio_pika.Message(
                body=payload_string.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await exchange.publish(
                message, routing_key=settings.app_rabbit_inbound_routing_key
            )
            logger.info(
                f"Published to inbound queue {payload_string}", payload=payload_string
            )
            return
