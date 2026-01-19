"""
Logging configuration and utilities.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from config.settings import settings


def setup_logger(
    name: str,
    log_dir: str | None = None,
) -> logging.Logger:
    """
    Create a component-specific logger using config.yaml settings.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # -------- Load logging config --------
    log_level = settings.get("logging.level", "INFO")
    log_file = settings.get("logging.log_file", "logs/app.log")
    max_bytes = settings.get("logging.max_bytes", 10 * 1024 * 1024)
    backup_count = settings.get("logging.backup_count", 5)

    logger.setLevel(getattr(logging, log_level))

    # -------- Resolve log directory --------
    if log_dir:
        log_path = Path(log_dir)
        log_file_path = log_path / "app.log"
    else:
        log_file_path = Path(log_file)
        log_path = log_file_path.parent

    log_path.mkdir(parents=True, exist_ok=True)

    # -------- File handler (rotating) --------
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )

    # -------- Console handler --------
    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
