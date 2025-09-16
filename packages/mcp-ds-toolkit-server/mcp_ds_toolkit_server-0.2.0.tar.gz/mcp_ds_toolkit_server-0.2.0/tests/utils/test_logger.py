"""Tests for the logger module."""

import logging
from unittest.mock import patch

import pytest

from mcp_ds_toolkit_server.utils.config import Settings
from mcp_ds_toolkit_server.utils.logger import make_logger, setup_logging


class TestMakeLogger:
    """Test cases for the make_logger function."""

    def test_make_logger_default(self):
        """Test creating a logger with default settings."""
        logger = make_logger("test_logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_make_logger_with_settings(self):
        """Test creating a logger with custom settings."""
        settings = Settings()
        settings.log_level = "DEBUG"

        logger = make_logger("test_logger_debug", settings)

        assert logger.level == logging.DEBUG

    def test_make_logger_idempotent(self):
        """Test that creating the same logger twice doesn't add duplicate handlers."""
        logger1 = make_logger("test_logger_idempotent")
        logger2 = make_logger("test_logger_idempotent")

        assert logger1 is logger2
        assert len(logger1.handlers) == 1

    def test_make_logger_different_names(self):
        """Test that different logger names create different loggers."""
        logger1 = make_logger("test_logger_1")
        logger2 = make_logger("test_logger_2")

        assert logger1 is not logger2
        assert logger1.name == "test_logger_1"
        assert logger2.name == "test_logger_2"


class TestSetupLogging:
    """Test cases for the setup_logging function."""

    def test_setup_logging_default(self):
        """Test setting up logging with default settings."""
        setup_logging()

        # Check that the mcp_mlops_server logger is configured correctly
        mcp_logger = logging.getLogger("mcp_mlops_server")
        assert mcp_logger.level == logging.INFO

    def test_setup_logging_with_settings(self):
        """Test setting up logging with custom settings."""
        settings = Settings()
        settings.log_level = "DEBUG"
        settings.debug = True

        setup_logging(settings)

        # Check that the mcp_mlops_server logger is set to DEBUG
        mcp_logger = logging.getLogger("mcp_mlops_server")
        assert mcp_logger.level == logging.DEBUG

    def test_setup_logging_third_party_levels(self):
        """Test that third-party library log levels are set correctly."""
        setup_logging()

        # Check that third-party loggers are set to WARNING
        assert logging.getLogger("urllib3").level == logging.WARNING
        assert logging.getLogger("requests").level == logging.WARNING
        assert logging.getLogger("sklearn").level == logging.WARNING
