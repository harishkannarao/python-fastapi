import asyncio
import json
from _asyncio import Task

import structlog
from aio_pika.abc import AbstractIncomingMessage, HeadersType
from fastapi.encoders import jsonable_encoder

from app.model.response.sample import Sample
from app.rabbit_mq.rabbit_mq_client import get_connection
from app.config import settings


async def process_retry_message_task(message: AbstractIncomingMessage):
    logger = structlog.get_logger()
    async with message.process():  # Automatically ACKs if no exception occurs
        payload_string: str = message.body.decode()
        headers = dict(message.headers) if message.headers else {}
        logger.info(
            f"Received retry message {payload_string}",
            payload=payload_string,
            headers=headers,
        )
        logger.info(
            f"Processed retry message {payload_string}",
            headers=headers,
            payload_string=payload_string,
        )


async def start_retry_consumer() -> Task[str]:
    logger = structlog.get_logger()
    # Create a dedicated channel for this consumer group
    channel = await get_connection().channel()
    # MAX CONCURRENCY SETTING: Limit unacknowledged messages on this channel
    await channel.set_qos(prefetch_count=settings.app_rabbit_consumer_concurrency)
    queue = await channel.get_queue(settings.app_rabbit_inbound_retry_queue)
    # Fire-and-forget the consumer loop into the background loop
    task: Task[str] = asyncio.create_task(queue.consume(process_retry_message_task))
    logger.info("Started retry message consumer")
    return task
