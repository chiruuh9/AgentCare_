"""
Database session management for AgentCare Type-2 Diabetes Decision Support System.

DISCLAIMER: AgentCare does NOT diagnose medical conditions or prescribe medications.
It is an administrative and clinical decision support system.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Create SQLite database engine
# connect_args={"check_same_thread": False} is required for SQLite with FastAPI multi-threading
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency helper for FastAPI endpoints to provide transactional database sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
