import aio_pika
import structlog
from aio_pika.abc import HeadersType

from app.config import settings
from app.rabbit_mq.rabbit_mq_client import get_connection


async def publish_to_inbound_retry(payload_string: str, headers: HeadersType = None):
    logger = structlog.get_logger()
    logger.info("Publishing to inbound retry queue ", payload_string=payload_string)
    async with get_connection().channel() as channel:
        exchange = await channel.get_exchange(
            settings.app_rabbit_inbound_retry_exchange
        )
        message = aio_pika.Message(
            body=payload_string.encode(),
            headers=headers,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Survives broker restart
        )
        await exchange.publish(
            message, routing_key=settings.app_rabbit_inbound_retry_routing_key
        )
        logger.info(
            f"Published to inbound retry queue {payload_string}", payload=payload_string
        )
        return
