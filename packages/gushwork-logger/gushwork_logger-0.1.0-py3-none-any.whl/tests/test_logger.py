"""
Test cases for gushwork_logger.
"""

import logging
import pytest
from unittest.mock import patch, MagicMock

from gushwork_logger import initialize_logging, get_logger, shutdown_logging, is_initialized


class TestGushworkLogger:
    def teardown_method(self):
        """Clean up after each test."""
        shutdown_logging()

    def test_basic_initialization(self):
        """Test basic logger initialization."""
        provider = initialize_logging(
            service_name="test-service",
            environment="test",
            enable_otlp=False  # Disable OTLP for testing
        )

        assert is_initialized()
        logger = get_logger(__name__)
        assert isinstance(logger, logging.Logger)

    def test_get_logger_without_init(self):
        """Test getting logger without explicit initialization."""
        logger = get_logger(__name__)
        assert isinstance(logger, logging.Logger)
        assert is_initialized()

    def test_multiple_initialization(self):
        """Test that multiple initialization calls don't cause issues."""
        provider1 = initialize_logging(service_name="test1", enable_otlp=False)
        provider2 = initialize_logging(service_name="test2", enable_otlp=False)

        # Should return the same provider (first initialization)
        assert provider1 == provider2

    @patch.dict('os.environ', {'AWS_LAMBDA_FUNCTION_NAME': 'test-lambda'})
    def test_lambda_environment(self):
        """Test initialization in AWS Lambda environment."""
        provider = initialize_logging(enable_otlp=False)
        assert is_initialized()

    def test_shutdown(self):
        """Test logger shutdown."""
        initialize_logging(enable_otlp=False)
        assert is_initialized()

        shutdown_logging()
        assert not is_initialized()

    @patch('gushwork_logger.logger.OTLPLogExporter')
    def test_otlp_initialization_failure(self, mock_exporter):
        """Test handling of OTLP initialization failure."""
        mock_exporter.side_effect = Exception("OTLP connection failed")

        provider = initialize_logging(enable_otlp=True)
        assert provider is None  # Should fall back gracefully
        assert is_initialized()

    def test_custom_log_level(self):
        """Test initialization with custom log level."""
        initialize_logging(log_level=logging.DEBUG, enable_otlp=False)

        logger = get_logger(__name__)
        assert logger.level == logging.DEBUG or logging.getLogger().level == logging.DEBUG