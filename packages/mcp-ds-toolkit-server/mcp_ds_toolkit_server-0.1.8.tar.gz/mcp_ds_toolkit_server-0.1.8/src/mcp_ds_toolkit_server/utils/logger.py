"""Logging utilities for the MCP MLOps server."""

import logging
import sys
from typing import Optional

from mcp_ds_toolkit_server.utils.config import Settings


def make_logger(name: str, settings: Optional[Settings] = None) -> logging.Logger:
    """Create a logger with the specified name and configuration.

    Args:
        name: Name of the logger.
        settings: Optional settings object. If None, creates a new one.

    Returns:
        Configured logger instance.
    """
    if settings is None:
        settings = Settings()

    logger = logging.getLogger(name)

    # Don't add handlers if they already exist
    if logger.handlers:
        return logger

    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create console handler - use stderr for MCP protocol compliance
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


def setup_logging(settings: Optional[Settings] = None) -> None:
    """Set up logging configuration for the entire application.

    Args:
        settings: Optional settings object. If None, creates a new one.
    """
    if settings is None:
        settings = Settings()

    # Configure root logger - use stderr for MCP protocol compliance
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    # Set specific log levels for third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("sklearn").setLevel(logging.WARNING)

    if settings.debug:
        logging.getLogger("mcp_mlops_server").setLevel(logging.DEBUG)
    else:
        logging.getLogger("mcp_mlops_server").setLevel(logging.INFO)
