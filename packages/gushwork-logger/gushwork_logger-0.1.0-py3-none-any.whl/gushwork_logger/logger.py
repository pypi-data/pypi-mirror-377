"""
Enhanced logger implementation with OpenTelemetry support and AWS Lambda compatibility.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

_logger_provider: Optional[LoggerProvider] = None
_initialized = False


def initialize_logging(
    service_name: Optional[str] = None,
    environment: Optional[str] = None,
    log_level: int = logging.INFO,
    enable_console: bool = True,
    enable_otlp: bool = True
) -> Optional[LoggerProvider]:
    """
    Initialize logging with OpenTelemetry support.

    Args:
        service_name: Name of the service (defaults to OTEL_SERVICE_NAME env var)
        environment: Environment name (defaults to ENVIRONMENT env var)
        log_level: Logging level (default: INFO)
        enable_console: Whether to enable console logging (default: True)
        enable_otlp: Whether to enable OTLP export (default: True)

    Returns:
        LoggerProvider instance if OTLP is successfully initialized, None otherwise
    """
    global _logger_provider, _initialized

    if _initialized:
        return _logger_provider

    load_dotenv()

    # Set up console handler if enabled and not in AWS Lambda
    if enable_console and not os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)

    logging.getLogger().setLevel(log_level)

    if enable_otlp:
        try:
            _logger_provider = LoggerProvider(
                resource=Resource.create({
                    "service.name": service_name or os.environ.get("OTEL_SERVICE_NAME", "gushwork-service"),
                    "service.environment": environment or os.environ.get("ENVIRONMENT", "dev")
                }),
            )
            set_logger_provider(_logger_provider)

            exporter = OTLPLogExporter()
            _logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
            handler = LoggingHandler(level=log_level, logger_provider=_logger_provider)

            logging.getLogger().addHandler(handler)
            print(f"OTLP logging initialized successfully for service: {service_name or 'gushwork-service'}")

        except Exception as e:
            print(f"Failed to initialize OTLP logging: {e}")
            print("Falling back to console-only logging")
            _logger_provider = None

    _initialized = True
    return _logger_provider


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance. Initializes logging if not already done.

    Args:
        name: Logger name (defaults to calling module name)

    Returns:
        Logger instance
    """
    if not _initialized:
        initialize_logging()

    return logging.getLogger(name)


def shutdown_logging() -> None:
    """
    Shutdown the logging system and clean up resources.
    """
    global _logger_provider, _initialized
    if _logger_provider:
        _logger_provider.shutdown()
    _initialized = False
    _logger_provider = None


def is_initialized() -> bool:
    """
    Check if logging has been initialized.

    Returns:
        True if logging is initialized, False otherwise
    """
    return _initialized


def get_logger_provider() -> Optional[LoggerProvider]:
    """
    Get the current logger provider instance.

    Returns:
        LoggerProvider instance or None if not initialized with OTLP
    """
    return _logger_provider