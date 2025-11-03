"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from backend.config import get_settings
from backend.models.base import Base

settings = get_settings()

# Create engine with connection pooling
# Optimized for PostgreSQL with multiple workers and concurrent requests
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,       # Verify connections before using
    pool_size=20,              # Base connection pool (increased from 10)
    max_overflow=30,           # Max overflow connections (increased from 20)
    pool_timeout=30,           # Wait 30 seconds for connection before failing
    pool_recycle=3600,         # Recycle connections after 1 hour (prevents stale connections)
    echo=False                 # Set to True for SQL query logging (debug only)
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions (for use outside FastAPI)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
