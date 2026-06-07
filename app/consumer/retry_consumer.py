import asyncio
from datetime import datetime, UTC
from _asyncio import Task

import structlog
from aio_pika.abc import AbstractIncomingMessage

from app.rabbit_mq.rabbit_mq_client import get_connection
from app.config import settings
from app.producer.inbound_retry_producer import publish_to_inbound_retry
from app.producer.inbound_producer import publish_to_inbound


async def process_retry_message_task(message: AbstractIncomingMessage):
    logger = structlog.get_logger("retry_consumer")
    async with message.process():  # Automatically ACKs if no exception occurs
        payload_string: str = message.body.decode()
        headers = dict(message.headers) if message.headers else {}
        logger.debug(
            f"Received retry message {payload_string}",
            payload=payload_string,
            headers=headers,
        )
        count: int = headers.get("count")
        next_retry: datetime = datetime.fromisoformat(headers.get("next_retry"))
        current_datetime = datetime.now(UTC)
        if (
            count <= settings.app_rabbit_inbound_max_retry
            and next_retry <= current_datetime
        ):
            await publish_to_inbound(payload_string=payload_string, headers=headers)
            logger.info(
                f"Sent to inbound queue {payload_string}",
                headers=headers,
                payload_string=payload_string,
            )
        elif (
            count <= settings.app_rabbit_inbound_max_retry
            and next_retry > datetime.now(UTC)
        ):
            await publish_to_inbound_retry(
                payload_string=payload_string, headers=headers
            )
            logger.debug(
                f"Sent to retry queue {payload_string}",
                headers=headers,
                payload_string=payload_string,
            )
        else:
            logger.info(
                f"Max retries exhausted, discarding message {payload_string}",
                payload=payload_string,
                headers=headers,
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
