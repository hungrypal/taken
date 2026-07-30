"""Central structured logging configuration for API and domain events."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging() -> logging.Logger:
    """Configure rotating application and error logs once per process."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("terrascore")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    for filename, level in (("app.log", logging.INFO), ("error.log", logging.ERROR)):
        handler = RotatingFileHandler(log_dir / filename, maxBytes=5_000_000, backupCount=5)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = configure_logging()
