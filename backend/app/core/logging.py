"""Logging configuration for MedLens."""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures root application logger with standard output formatting."""
    log_format = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger("medlens")
    return logger


logger = setup_logging()
