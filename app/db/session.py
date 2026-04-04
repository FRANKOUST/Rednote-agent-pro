from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base

_ENGINE = None
_SESSION_FACTORY = None


def get_engine():
    global _ENGINE
    if _ENGINE is None:
        settings = get_settings()
        connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
        _ENGINE = create_engine(settings.database_url, future=True, connect_args=connect_args)
    return _ENGINE


def get_session_factory():
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        _SESSION_FACTORY = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)
    return _SESSION_FACTORY


def init_db() -> None:
    Base.metadata.create_all(bind=get_engine())


@contextmanager
def session_scope() -> Session:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_db_state() -> None:
    global _ENGINE, _SESSION_FACTORY
    _ENGINE = None
    _SESSION_FACTORY = None
    get_settings.cache_clear()
