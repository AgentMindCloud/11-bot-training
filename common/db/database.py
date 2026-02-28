"""SQLAlchemy database setup with context-manager session support."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from infra.config import settings


class Base(DeclarativeBase):
    pass


def get_engine(database_url: str | None = None):
    url = database_url or settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, echo=False)


def get_session_factory(database_url: str | None = None):
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session(database_url: str | None = None) -> Generator[Session, None, None]:
    """Context manager that yields a SQLAlchemy session and handles cleanup."""
    factory = get_session_factory(database_url)
    session: Session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
