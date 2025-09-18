"""Logging configuration for the GitHub IOC Scanner."""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    include_timestamp: bool = True,
    log_file: Optional[str] = None
) -> None:
    """
    Configure logging for the GitHub IOC Scanner.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        include_timestamp: Whether to include timestamps in log messages
        log_file: Optional file path to write logs to (in addition to console)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Default format string
    if format_string is None:
        if include_timestamp:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            format_string = "%(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[]  # We'll add handlers manually
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(console_formatter)
    
    # Get root logger and add console handler
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            logging.warning(f"Could not create log file {log_file}: {e}")
    
    # Set specific logger levels for external libraries to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    Change the log level for all loggers.
    
    Args:
        level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Update root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(numeric_level)


def log_exception(logger: logging.Logger, message: str, exc: Exception) -> None:
    """
    Log an exception with full traceback information.
    
    Args:
        logger: Logger instance to use
        message: Descriptive message about the error context
        exc: Exception instance to log
    """
    logger.error(f"{message}: {exc}", exc_info=True)


def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs) -> None:
    """
    Log performance information for operations.
    
    Args:
        logger: Logger instance to use
        operation: Name of the operation
        duration: Duration in seconds
        **kwargs: Additional context information
    """
    context = " ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"Performance: {operation} completed in {duration:.3f}s {context}".strip())


def log_rate_limit(logger: logging.Logger, remaining: int, reset_time: int) -> None:
    """
    Log GitHub API rate limit information only when relevant (low or exhausted).
    
    Args:
        logger: Logger instance to use
        remaining: Number of requests remaining
        reset_time: Unix timestamp when rate limit resets
    """
    from datetime import datetime
    
    # Only log rate limit info when it's getting low or critical
    if remaining <= 0:
        # Rate limit exhausted - critical warning
        reset_datetime = datetime.fromtimestamp(reset_time)
        logger.warning(f"⚠️  Rate limit exhausted! Resets at {reset_datetime}")
    elif remaining <= 100:
        # Rate limit getting low - warning
        reset_datetime = datetime.fromtimestamp(reset_time)
        logger.warning(f"⚠️  Rate limit low: {remaining} requests remaining, resets at {reset_datetime}")
    elif remaining <= 500:
        # Rate limit moderately low - info only in verbose mode
        reset_datetime = datetime.fromtimestamp(reset_time)
        logger.info(f"Rate limit: {remaining} requests remaining, resets at {reset_datetime}")
    # For remaining > 500, don't log anything (normal operation)


def log_cache_stats(logger: logging.Logger, hits: int, misses: int, hit_rate: float) -> None:
    """
    Log cache performance statistics.
    
    Args:
        logger: Logger instance to use
        hits: Number of cache hits
        misses: Number of cache misses
        hit_rate: Cache hit rate as percentage
    """
    logger.info(f"Cache stats: {hits} hits, {misses} misses, {hit_rate:.1f}% hit rate")