"""Lazy Google Earth Engine initialization helper."""

from __future__ import annotations

import os
from threading import Lock

import ee
from dotenv import load_dotenv

from backend.utils.logger import logger


_earth_engine_lock = Lock()
_earth_engine_initialized = False


def initialize_earth_engine() -> bool:
    """Initialize Google Earth Engine once, on demand.

    Returns True when EE is ready and False when initialization could not be
    completed. Errors are logged instead of being raised so FastAPI can keep
    starting without Earth Engine credentials.
    """
    global _earth_engine_initialized

    with _earth_engine_lock:
        if _earth_engine_initialized:
            return True

        load_dotenv()
        project_id = os.getenv("PROJECT_ID")

        if not project_id:
            logger.error("Earth Engine initialization skipped because PROJECT_ID is not set.")
            return False

        try:
            ee.Initialize(project=project_id)
        except Exception:
            logger.exception("Earth Engine initialization failed for project_id=%s", project_id)
            return False

        _earth_engine_initialized = True
        logger.info("Earth Engine initialized successfully for project_id=%s", project_id)
        return True