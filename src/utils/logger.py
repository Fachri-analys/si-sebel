"""
Logging utility for Si Sebel Bot.
Provides structured logging with color support for console output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from colorlog import ColoredFormatter
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


class Logger:
    """Custom logger with color support and file logging."""

    _loggers = {}

    @classmethod
    def get_logger(
        cls,
        name: str,
        log_level: str = "INFO",
        log_file: Optional[str] = None
    ) -> logging.Logger:
        """
        Get or create a logger instance.

        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional path to log file

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        if COLORLOG_AVAILABLE:
            console_format = ColoredFormatter(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                }
            )
        else:
            console_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        # File handler (if log_file is provided)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

def setup_application_logger(
    app_name: str = "sisebel",
    log_level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup main application logger.

    Args:
        app_name: Application name
        log_level: Logging level
        log_file: Optional path to log file

    Returns:
        Configured application logger
    """
    return Logger.get_logger(app_name, log_level, log_file)