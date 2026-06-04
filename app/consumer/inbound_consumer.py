import asyncio
import json
import uuid
from _asyncio import Task
from typing import Any

import structlog
from aio_pika.abc import AbstractIncomingMessage
from fastapi.encoders import jsonable_encoder

from app.config import settings
from app.model.response.sample import Sample
from app.producer.inbound_retry_producer import publish_to_inbound_retry
from app.producer.outbound_producer import publish_to_outbound
from app.rabbit_mq.rabbit_mq_client import get_connection


async def process_inbound_message_task(message: AbstractIncomingMessage):
    logger = structlog.get_logger()
    async with message.process():  # Automatically ACKs if no exception occurs
        try:
            payload_string: str = message.body.decode()
            headers = dict(message.headers) if message.headers else {}
            count: int = headers.get("count", 1)
            message_id: str = headers.get("message_id", str(uuid.uuid4()))
            message_context: dict[str, Any] = {"message_id": message_id, "count": count}
            custom_logger = logger.bind(**message_context)
            custom_logger.info(
                f"Received inbound message {payload_string}",
                payload=payload_string,
                headers=headers,
            )
            samples = [Sample(**item) for item in json.loads(payload_string)]
            await publish_to_outbound(samples=samples, headers=headers)
            custom_logger.info(
                f"Processed inbound message {payload_string}",
                headers=headers,
                samples=jsonable_encoder(samples),
            )
        except Exception as e:
            logger.error(
                f"Unexpected Exception!: {repr(e)}",
                payload_string=payload_string,
                headers=headers,
            )
            if samples is None:
                logger.error(
                    f"Unable to parse raw payload {payload_string}",
                    payload_string=payload_string,
                    headers=headers,
                )
            else:
                headers.update({"count": count + 1, "message_id": message_id})
                await publish_to_inbound_retry(samples=samples, headers=headers)


async def start_inbound_consumer() -> Task[str]:
    logger = structlog.get_logger()
    # Create a dedicated channel for this consumer group
    channel = await get_connection().channel()
    # MAX CONCURRENCY SETTING: Limit unacknowledged messages on this channel
    await channel.set_qos(prefetch_count=settings.app_rabbit_consumer_concurrency)
    queue = await channel.get_queue(settings.app_rabbit_inbound_queue)
    # Fire-and-forget the consumer loop into the background loop
    task: Task[str] = asyncio.create_task(queue.consume(process_inbound_message_task))
    logger.info("Started inbound message consumer")
    return task
