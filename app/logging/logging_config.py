import logging
import sys

import structlog
from structlog.contextvars import merge_contextvars
from structlog.stdlib import LoggerFactory


def setup_logging(json_logs: bool = False):
    shared_processors = [
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.add_log_level,
        merge_contextvars,
    ]

    if json_logs:
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

    structlog.configure(
        processors=processors,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
