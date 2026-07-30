"""Compatibility export for projects expecting ``backend.database.database``."""

from backend.database.session import Base, SessionLocal, engine, get_db, init_database

__all__ = ["Base", "SessionLocal", "engine", "get_db", "init_database"]
