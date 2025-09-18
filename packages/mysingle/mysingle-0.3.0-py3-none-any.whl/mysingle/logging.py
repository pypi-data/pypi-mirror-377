"""Centralized logging configuration for all services."""

import logging
import sys
from typing import Optional

from pydantic import BaseModel


class LogConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    service_name: Optional[str] = None


def setup_logging(
    service_name: Optional[str] = None,
    level: str = "INFO",
    log_format: Optional[str] = None,
) -> None:
    """Configure centralized logging for services.

    Args:
        service_name: Name of the service for log identification
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
    """
    # Default format with service name
    if log_format is None:
        if service_name:
            log_format = f"%(asctime)s - {service_name} - %(name)s - %(levelname)s - %(message)s"
        else:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        stream=sys.stdout,
        force=True,  # Override any existing configuration
    )

    # Set specific loggers to appropriate levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("beanie").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)

    if service_name:
        logger = logging.getLogger(service_name)
        logger.info("Logging configured for service: %s", service_name)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
