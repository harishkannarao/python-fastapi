from typing import Optional

import aio_pika
import structlog
from aio_pika.abc import AbstractRobustConnection

from app.config import settings

# This acts as our global registry inside the application space
_connection: Optional[AbstractRobustConnection] = None


async def open_rabbit_connection() -> None:
    logger = structlog.get_logger()

    logger.info(
        f"Connecting to RabbitMQ at {settings.app_rabbit_mq_host}:{settings.app_rabbit_mq_port}..."
    )

    rabbit_mq_url = (
        f"amqp://{settings.app_rabbit_mq_username}:{settings.app_rabbit_mq_password}"
        f"@{settings.app_rabbit_mq_host}:{settings.app_rabbit_mq_port}/{settings.app_rabbit_mq_vhost}"
    )

    connection = await aio_pika.connect_robust(rabbit_mq_url)
    logger.info(
        f"Successfully Connected to RabbitMQ at {settings.app_rabbit_mq_host}:{settings.app_rabbit_mq_port}..."
    )
    """Sets the global connection instance during startup."""
    global _connection

    _connection = connection


async def close_rabbit_connection() -> None:
    logger = structlog.get_logger()

    logger.info(
        f"Closing connection to RabbitMQ at {settings.app_rabbit_mq_host}:{settings.app_rabbit_mq_port}..."
    )
    """
        Retrieves the active connection.
        Raises a runtime error if accessed before initialization.
        """
    if _connection is None or _connection.is_closed:
        raise RuntimeError(
            "RabbitMQ connection is not initialized or has been closed. "
            "Ensure 'set_connection' was called during app startup."
        )
    await _connection.close()
    logger.info(
        f"Successfully Disconnected from RabbitMQ at {settings.app_rabbit_mq_host}:{settings.app_rabbit_mq_port}..."
    )
    return


def get_connection() -> AbstractRobustConnection:
    """
    Retrieves the active connection.
    Raises a runtime error if accessed before initialization.
    """
    if _connection is None or _connection.is_closed:
        raise RuntimeError(
            "RabbitMQ connection is not initialized or has been closed. "
            "Ensure 'set_connection' was called during app startup."
        )
    return _connection
