"""
SQLAlchemy base configuration for Smart City Platform.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.pool import NullPool


class Base(DeclarativeBase):
    """Declarative base for all models."""
    pass


def get_engine(database_url: str | None = None):
    """Create SQLAlchemy engine."""
    if database_url is None:
        from config.settings import DATABASE_URL
        database_url = DATABASE_URL
    return create_engine(database_url, poolclass=NullPool, echo=False)


def get_session_factory(database_url: str | None = None):
    """Create session factory."""
    engine = get_engine(database_url)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session(database_url: str | None = None) -> Session:
    """Get a new database session."""
    factory = get_session_factory(database_url)
    return factory()
