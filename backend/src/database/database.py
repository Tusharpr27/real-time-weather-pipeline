"""
Database connection and session management
Provides database engine and session factory
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool

from config import settings
from src.database.models import Base


def get_database_engine():
    """
    Create and return SQLAlchemy engine
    Uses connection pooling for efficiency
    """
    # Use StaticPool for SQLite (in-memory friendly)
    # Use QueuePool for PostgreSQL (production)
    
    if "sqlite" in settings.database_url:
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
    else:
        engine = create_engine(
            settings.database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            **settings.database_engine_kwargs
        )
    
    return engine


def init_db():
    """Initialize database - create all tables"""
    engine = get_database_engine()
    Base.metadata.create_all(bind=engine)
    return engine


# Create engine instance
engine = init_db()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Session:
    """
    Dependency for FastAPI to get database session
    Usage in endpoints:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_session() -> Session:
    """Create and return a new database session"""
    return SessionLocal()


def get_engine():
    """Get database engine for direct access"""
    return engine
