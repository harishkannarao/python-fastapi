import aio_pika
import structlog

from app.config import settings
from app.rabbit_mq.rabbit_mq_client import get_connection


async def configure_rabbitmq():
    logger = structlog.get_logger()

    async with await get_connection().channel() as channel:
        logger.info("Configuring queues and exchanges")

        inbound_queue = await channel.declare_queue(
            settings.app_rabbit_inbound_queue,
            durable=settings.app_rabbit_mq_durable,
            arguments={
                "x-dead-letter-exchange": f"{settings.app_rabbit_inbound_queue}.dlx",
                "x-dead-letter-routing-key": f"{settings.app_rabbit_inbound_queue}.dlq.rk",
            },
        )

        inbound_exchange = await channel.declare_exchange(
            settings.app_rabbit_inbound_exchange,
            type=aio_pika.ExchangeType.TOPIC,
            durable=settings.app_rabbit_mq_durable,
        )

        await inbound_queue.bind(
            inbound_exchange, routing_key=settings.app_rabbit_inbound_routing_key
        )

        inbound_dead_queue = await channel.declare_queue(
            f"{settings.app_rabbit_inbound_queue}.dlq",
            durable=settings.app_rabbit_mq_durable,
        )

        inbound_dead_exchange = await channel.declare_exchange(
            f"{settings.app_rabbit_inbound_queue}.dlx",
            type=aio_pika.ExchangeType.TOPIC,
            durable=settings.app_rabbit_mq_durable,
        )

        await inbound_dead_queue.bind(
            inbound_dead_exchange,
            routing_key=f"{settings.app_rabbit_inbound_queue}.dlq.rk",
        )

        inbound_retry_queue = await channel.declare_queue(
            settings.app_rabbit_inbound_retry_queue,
            durable=settings.app_rabbit_mq_durable,
            arguments={
                "x-dead-letter-exchange": f"{settings.app_rabbit_inbound_retry_queue}.dlx",
                "x-dead-letter-routing-key": f"{settings.app_rabbit_inbound_retry_queue}.dlq.rk",
            },
        )

        inbound_retry_exchange = await channel.declare_exchange(
            settings.app_rabbit_inbound_retry_exchange,
            type=aio_pika.ExchangeType.TOPIC,
            durable=settings.app_rabbit_mq_durable,
        )

        await inbound_retry_queue.bind(
            inbound_retry_exchange,
            routing_key=settings.app_rabbit_inbound_retry_exchange,
        )

        inbound_retry_dead_queue = await channel.declare_queue(
            f"{settings.app_rabbit_inbound_retry_queue}.dlq",
            durable=settings.app_rabbit_mq_durable,
        )

        inbound_retry_dead_exchange = await channel.declare_exchange(
            f"{settings.app_rabbit_inbound_retry_queue}.dlx",
            type=aio_pika.ExchangeType.TOPIC,
            durable=settings.app_rabbit_mq_durable,
        )

        await inbound_retry_dead_queue.bind(
            inbound_retry_dead_exchange,
            routing_key=f"{settings.app_rabbit_inbound_retry_queue}.dlq.rk",
        )

        outbound_queue = await channel.declare_queue(
            settings.app_rabbit_outbound_queue,
            durable=settings.app_rabbit_mq_durable,
            arguments={
                "x-dead-letter-exchange": f"{settings.app_rabbit_outbound_queue}.dlx",
                "x-dead-letter-routing-key": f"{settings.app_rabbit_outbound_queue}.dlq.rk",
            },
        )

        outbound_exchange = await channel.declare_exchange(
            settings.app_rabbit_outbound_exchange,
            type=aio_pika.ExchangeType.TOPIC,
            durable=settings.app_rabbit_mq_durable,
        )

        await outbound_queue.bind(
            outbound_exchange, routing_key=settings.app_rabbit_outbound_routing_key
        )

        outbound_dead_queue = await channel.declare_queue(
            f"{settings.app_rabbit_outbound_queue}.dlq",
            durable=settings.app_rabbit_mq_durable,
        )

        outbound_dead_exchange = await channel.declare_exchange(
            f"{settings.app_rabbit_outbound_queue}.dlx",
            type=aio_pika.ExchangeType.TOPIC,
            durable=settings.app_rabbit_mq_durable,
        )

        await outbound_dead_queue.bind(
            outbound_dead_exchange,
            routing_key=f"{settings.app_rabbit_outbound_queue}.dlq.rk",
        )

        logger.info("Configuring queues and exchanges completed successfully")
