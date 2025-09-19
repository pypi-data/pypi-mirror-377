"""
Gushwork Logger - A structured logging library with OpenTelemetry support.
"""

from .logger import initialize_logging, get_logger, shutdown_logging, is_initialized, get_logger_provider

__version__ = "0.1.0"
__all__ = ["initialize_logging", "get_logger", "shutdown_logging", "is_initialized", "get_logger_provider"]