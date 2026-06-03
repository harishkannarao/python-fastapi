import json

import aio_pika
import structlog
from fastapi.encoders import jsonable_encoder

from app.rabbit_mq.rabbit_mq_client import get_connection
from app.model.response.sample import Sample
from app.config import settings


async def publish_to_inbound_retry(samples: list[Sample]):
    logger = structlog.get_logger()
    logger.info("Publishing to inbound retry queue ", samples=samples)
    async with get_connection().channel() as channel:
        exchange = await channel.get_exchange(
            settings.app_rabbit_inbound_retry_exchange
        )
        payload_string: str = json.dumps(jsonable_encoder(samples))
        message = aio_pika.Message(
            body=payload_string.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Survives broker restart
        )
        await exchange.publish(
            message, routing_key=settings.app_rabbit_inbound_retry_routing_key
        )
        logger.info(
            f"Published to inbound retry queue {payload_string}", payload=payload_string
        )
        return
