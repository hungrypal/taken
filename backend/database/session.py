"""SQLAlchemy database setup shared by API routes and services."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM entities."""


engine_options: dict = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    # SQLite connections must stay usable when FastAPI runs sync handlers in
    # worker threads.
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """Yield one transaction-scoped session and always release it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    # Import all models before metadata is evaluated.
    

    # Import all models before metadata is evaluated. In production, prefer
    # Alembic migrations; this keeps a fresh SQLite developer setup usable.
    import backend.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
