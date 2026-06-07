import logging
import sys

import structlog
from structlog.processors import CallsiteParameterAdder, CallsiteParameter
from structlog.contextvars import merge_contextvars
from structlog.stdlib import LoggerFactory

from app.config import Settings


def setup_logging(settings: Settings):
    shared_processors = [
        CallsiteParameterAdder(
            {
                CallsiteParameter.PATHNAME,  # e.g., "/app/app.py"
                CallsiteParameter.FILENAME,  # e.g., "app.py"
                CallsiteParameter.FUNC_NAME,  # e.g., "my_function"
                CallsiteParameter.LINENO,  # e.g., 42
            }
        ),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.add_log_level,
        merge_contextvars,
    ]

    if settings.app_json_logs:
        log_renderer = structlog.processors.JSONRenderer()
    else:
        log_renderer = structlog.dev.ConsoleRenderer()

    processors = shared_processors + [
        log_renderer,
    ]

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    if settings.app_db_log_sql:
        logging.getLogger("databases").setLevel(logging.DEBUG)

    if settings.app_retry_consumer_log_debug:
        logging.getLogger("retry_consumer").setLevel(logging.DEBUG)

    structlog.configure(
        processors=processors,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
