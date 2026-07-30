"""Production ASGI entrypoint.

Run with: ``uvicorn backend.main:app``.
``backend.api:app`` remains supported for existing deployments.
"""

from backend.api import app

__all__ = ["app"]
