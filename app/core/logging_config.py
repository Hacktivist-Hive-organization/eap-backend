# app/core/logging_config.py

import logging
import sys

import structlog

from app.core.config import settings

APP_ENV = settings.APP_ENV
LOG_LEVEL = settings.LOG_LEVEL


def configure_logging() -> None:
    """
    Configure application-wide logging.
    This should be called once, when the app starts.
    """

    logging.basicConfig(
        level=LOG_LEVEL.upper(),
        stream=sys.stdout,
        format="%(message)s",
    )

    #  Shared processors (used in all environments)
    shared_processors = [
        structlog.contextvars.merge_contextvars,  # add request context
        structlog.processors.add_log_level,  # add log level
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),  # include stack info if available
        structlog.processors.format_exc_info,  # format exception info
    ]

    #  Environment-based rendering
    if APP_ENV == "development":
        processors = shared_processors + [structlog.dev.ConsoleRenderer()]
    else:
        processors = shared_processors + [structlog.processors.JSONRenderer()]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            logging._nameToLevel[LOG_LEVEL.upper()]
        ),
        cache_logger_on_first_use=True,
    )
