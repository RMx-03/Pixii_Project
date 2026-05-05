"""Database engine and session handling."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base class for SQLAlchemy models."""


settings = get_settings()
is_sqlite = settings.database_url.startswith("sqlite")
engine = create_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=not is_sqlite,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for request lifetime."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
