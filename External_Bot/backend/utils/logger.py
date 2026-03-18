"""
Logging Configuration and Utilities
====================================

This module sets up a centralized logging system for the application.
All components can use this logger for consistent, traceable logging across the application.

Features:
    - Configured to log to both console and file
    - Different log levels for development vs production
    - Consistent message formatting with timestamp and level indicators
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger instance with console and file handlers.
    
    This function sets up a logger with a standardized format that includes
    timestamps, log levels, and module names. Logs are written to both the
    console (for real-time monitoring) and a log file (for persistent records).
    
    Args:
        name (str): The name of the logger (typically __name__ from the calling module)
        level (int, optional): The logging level to use. Defaults to logging.INFO.
                             Common values: logging.DEBUG, logging.INFO, logging.WARNING
    
    Returns:
        logging.Logger: A configured logger instance ready to use
    
    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Application started")
        >>> logger.error("An error occurred", exc_info=True)
    """
    # Create logger with the specified name
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding duplicate handlers if logger is configured multiple times
    if logger.handlers:
        return logger
    
    # Define the log message format with timestamp, level, name and message
    # Format: [TIMESTAMP] LEVEL - LOGGER_NAME - MESSAGE
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler: outputs logs to terminal/console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler: outputs logs to a file for persistent storage
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp to track different sessions
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Create module-level logger for direct imports
logger = setup_logger(__name__)
