"""
Logging utilities for AgentSpec.

Provides structured logging setup with configuration support,
context managers for operation logging, and appropriate formatters.
"""

import json
import logging
import logging.config
import os
import sys
import traceback
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from ..config import get_logging_config_path


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            ):
                log_data[key] = value

        return json.dumps(log_data, default=str)


class ContextFilter(logging.Filter):
    """Filter to add context information to log records."""

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.context = context or {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context information to log record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True

    def update_context(self, context: Dict[str, Any]) -> None:
        """Update the context information."""
        self.context.update(context)


class AgentSpecLogger:
    """Logger with context management and structured logging."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context_filter = ContextFilter()
        self.logger.addFilter(self.context_filter)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with optional context."""
        self._log_with_context(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with optional context."""
        self._log_with_context(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with optional context."""
        self._log_with_context(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with optional context."""
        self._log_with_context(logging.ERROR, message, kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with optional context."""
        self._log_with_context(logging.CRITICAL, message, kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        kwargs["exc_info"] = True
        self._log_with_context(logging.ERROR, message, kwargs)

    def _log_with_context(
        self, level: int, message: str, context: Dict[str, Any]
    ) -> None:
        """Log message with context information."""
        # Temporarily update context
        old_context = self.context_filter.context.copy()
        self.context_filter.update_context(context)

        try:
            self.logger.log(level, message)
        finally:
            # Restore original context
            self.context_filter.context = old_context

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set persistent context for this logger."""
        self.context_filter.update_context(context)

    def clear_context(self) -> None:
        """Clear all context information."""
        self.context_filter.context.clear()


def get_log_directory() -> Optional[Path]:
    """
    Get the directory where log files should be stored.

    Returns the installation directory of agentspec if debug logging is enabled,
    otherwise returns None to disable file logging.
    """
    # Only create log files if debug logging is explicitly enabled
    if not os.getenv("AGENTSPEC_DEBUG_LOGGING"):
        return None

    # Use the directory where the agentspec package is installed
    package_dir = Path(__file__).parent.parent
    log_dir = package_dir / "logs"

    # Create logs directory if it doesn't exist
    log_dir.mkdir(exist_ok=True)

    return log_dir


def setup_logging(
    config_path: Optional[Path] = None,
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    structured: bool = False,
    console_output: bool = True,
) -> None:
    """
    Set up logging configuration for AgentSpec.

    Args:
        config_path: Path to logging configuration file
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (overrides environment-based file logging)
        structured: Whether to use structured JSON logging
        console_output: Whether to output to console
    """
    # Check if file logging should be enabled
    log_dir = get_log_directory()
    enable_file_logging = log_dir is not None or log_file is not None

    # Use default config if none provided
    if config_path is None:
        config_path = get_logging_config_path()

    # Load logging configuration
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            if enable_file_logging:
                # Update file handler paths to use log directory
                if log_dir and "handlers" in config:
                    if "file" in config["handlers"]:
                        config["handlers"]["file"]["filename"] = str(
                            log_dir / "agentspec.log"
                        )
                    if "error_file" in config["handlers"]:
                        config["handlers"]["error_file"]["filename"] = str(
                            log_dir / "agentspec_errors.log"
                        )
            else:
                # Remove file handlers from configuration when file logging is disabled
                if "handlers" in config:
                    # Remove file handlers
                    config["handlers"].pop("file", None)
                    config["handlers"].pop("error_file", None)

                # Update logger configurations to remove file handler references
                if "loggers" in config:
                    for logger_name, logger_config in config["loggers"].items():
                        if "handlers" in logger_config:
                            # Remove file handlers from handler lists
                            handlers = logger_config["handlers"]
                            if isinstance(handlers, list):
                                logger_config["handlers"] = [
                                    h
                                    for h in handlers
                                    if h not in ["file", "error_file"]
                                ]

            logging.config.dictConfig(config)
        except (yaml.YAMLError, KeyError) as e:
            # Fall back to basic configuration
            _setup_basic_logging(
                log_level,
                log_file or (log_dir / "agentspec.log" if log_dir else None),
                structured,
                console_output,
            )
            logging.warning(f"Failed to load logging config from {config_path}: {e}")
    else:
        # Setup basic logging without file handlers if file logging is disabled
        effective_log_file = log_file
        if not log_file and log_dir:
            effective_log_file = log_dir / "agentspec.log"
        _setup_basic_logging(log_level, effective_log_file, structured, console_output)

    # Override log level if specified
    if log_level:
        logging.getLogger("agentspec").setLevel(getattr(logging, log_level.upper()))

    # Log startup message only if file logging is enabled
    if enable_file_logging:
        logger = get_logger("agentspec.logging")
        logger.info(
            "Logging system initialized",
            config_path=str(config_path),
            log_level=log_level,
            structured=structured,
            log_directory=str(log_dir) if log_dir else "custom",
        )


def _setup_basic_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    structured: bool = False,
    console_output: bool = True,
) -> None:
    """Set up basic logging configuration."""
    level = getattr(logging, (log_level or "INFO").upper())

    # Create formatters
    formatter: logging.Formatter
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Add console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Add file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> AgentSpecLogger:
    """Get a logger instance."""
    return AgentSpecLogger(name)


@contextmanager
def log_operation(
    logger: Union[AgentSpecLogger, logging.Logger],
    operation: str,
    **context: Any,
) -> Any:
    """
    Context manager for logging operations with timing and error handling.

    Args:
        logger: Logger instance to use
        operation: Name of the operation being performed
        **context: Additional context to include in logs
    """
    start_time = datetime.utcnow()

    if isinstance(logger, AgentSpecLogger):
        logger.info(f"Starting {operation}", operation=operation, **context)
    else:
        logger.info(f"Starting {operation}")

    try:
        yield

        duration = (datetime.utcnow() - start_time).total_seconds()
        if isinstance(logger, AgentSpecLogger):
            logger.info(
                f"Completed {operation}",
                operation=operation,
                duration=duration,
                **context,
            )
        else:
            logger.info(f"Completed {operation} in {duration:.2f}s")

    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        if isinstance(logger, AgentSpecLogger):
            logger.error(
                f"Failed {operation}: {e}",
                operation=operation,
                duration=duration,
                error_type=type(e).__name__,
                **context,
            )
        else:
            logger.error(f"Failed {operation} after {duration:.2f}s: {e}")
        raise


@contextmanager
def log_context(logger: AgentSpecLogger, **context: Any) -> Any:
    """
    Context manager for temporarily setting logger context.

    Args:
        logger: AgentSpecLogger instance
        **context: Context to set temporarily
    """
    old_context = logger.context_filter.context.copy()
    logger.set_context(context)

    try:
        yield
    finally:
        logger.context_filter.context = old_context


def configure_third_party_loggers() -> None:
    """Configure third-party library loggers to reduce noise."""
    # Reduce noise from common libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("yaml").setLevel(logging.WARNING)
    logging.getLogger("jsonschema").setLevel(logging.WARNING)


# Module-level logger for this module
_logger = get_logger(__name__)


def get_logger_with_context(name: str, **context: Any) -> AgentSpecLogger:
    """
    Get a logger instance with pre-set context.

    Args:
        name: Logger name
        **context: Context to set on the logger

    Returns:
        AgentSpecLogger with context set
    """
    logger = get_logger(name)
    logger.set_context(context)
    return logger


def log_performance(
    logger: Union[AgentSpecLogger, logging.Logger],
    operation: str,
    duration: float,
    **context: Any,
) -> None:
    """
    Log performance information for an operation.

    Args:
        logger: Logger instance to use
        operation: Name of the operation
        duration: Duration in seconds
        **context: Additional context to include
    """
    if isinstance(logger, AgentSpecLogger):
        logger.info(
            f"Performance: {operation} took {duration:.3f}s",
            operation=operation,
            duration=duration,
            performance=True,
            **context,
        )
    else:
        logger.info(f"Performance: {operation} took {duration:.3f}s")
