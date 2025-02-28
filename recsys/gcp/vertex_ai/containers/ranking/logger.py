"""
Custom logger configuration for ranking container.
"""

import logging
import sys
import time
import uuid
from typing import Optional

# Emoji mapping for log levels
EMOJI_MAP = {
    "DEBUG": "🔍",
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "🚨",
    "SUCCESS": "✅",
    "TIMER": "⏱️",
    "QUERY": "🔎",
    "MODEL": "🤖",
    "DATA": "📊",
}

# ANSI color codes for terminal output
COLORS = {
    "RESET": "\033[0m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
}


class RequestContext:
    """Thread-local storage for request-specific data."""

    _request_id = None
    _start_time = None

    @classmethod
    def set_request_id(cls, request_id: Optional[str] = None):
        """Set request ID for the current thread."""
        cls._request_id = request_id or str(uuid.uuid4())
        cls._start_time = time.time()
        return cls._request_id

    @classmethod
    def get_request_id(cls):
        """Get request ID for the current thread."""
        if cls._request_id is None:
            cls.set_request_id()
        return cls._request_id

    @classmethod
    def get_elapsed_time(cls):
        """Get elapsed time since the request started."""
        if cls._start_time is None:
            return 0
        return time.time() - cls._start_time


class CustomFormatter(logging.Formatter):
    """Custom formatter for logs with emoji and colors."""

    def format(self, record):
        # Get the appropriate emoji
        emoji = EMOJI_MAP.get(record.levelname, "")

        # Get the appropriate color
        if record.levelno >= logging.ERROR:
            color = COLORS["RED"]
        elif record.levelno >= logging.WARNING:
            color = COLORS["YELLOW"]
        elif record.levelno >= logging.INFO:
            color = COLORS["GREEN"]
        else:
            color = COLORS["BLUE"]

        # Add request_id if available
        request_id = getattr(record, "request_id", RequestContext.get_request_id())
        request_time = getattr(
            record, "elapsed_time", RequestContext.get_elapsed_time()
        )

        # Format the time
        log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))

        # Combine all parts
        log_message = (
            f"{color}{log_time} {emoji} "
            f"[{record.levelname}] "
            f"[REQ:{request_id[:8]}] "
            f"[{request_time:.3f}s] "
            f"{record.getMessage()}{COLORS['RESET']}"
        )

        # Add exception info if present
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            if record.exc_text:
                log_message = f"{log_message}\n{record.exc_text}"

        return log_message


def setup_logger(name="ranking-service", level=logging.INFO):
    """Set up and configure logger with custom formatting."""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter
    formatter = CustomFormatter()

    # Add formatter to handler
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


# Custom log levels and methods
def success(self, message, *args, **kwargs):
    """Log a success message."""
    self.info(f"✅ {message}", *args, **kwargs)


def timer_start(self, operation_name):
    """Start timing an operation."""
    setattr(self, f"_timer_{operation_name}", time.time())
    self.debug(f"⏱️ Started {operation_name}")


def timer_end(self, operation_name):
    """End timing an operation and log the duration."""
    start_time = getattr(self, f"_timer_{operation_name}", None)
    if start_time:
        duration = time.time() - start_time
        self.info(f"⏱️ {operation_name} completed in {duration:.3f}s")
        delattr(self, f"_timer_{operation_name}")
    else:
        self.warning(f"⏱️ No start time found for {operation_name}")


def query(self, query_text, *args, **kwargs):
    """Log a database query."""
    # Truncate long queries for readability
    if len(query_text) > 300:
        query_text = query_text[:300] + "..."
    self.debug(f"🔎 Executing query: {query_text}", *args, **kwargs)


def model(self, message, *args, **kwargs):
    """Log model-related information."""
    self.info(f"🤖 {message}", *args, **kwargs)


def data(self, message, *args, **kwargs):
    """Log data-related information."""
    self.info(f"📊 {message}", *args, **kwargs)


# Add custom methods to the Logger class
logging.Logger.success = success
logging.Logger.timer_start = timer_start
logging.Logger.timer_end = timer_end
logging.Logger.query = query
logging.Logger.model = model
logging.Logger.data = data

# Default logger instance
logger = setup_logger()
