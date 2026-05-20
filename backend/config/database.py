from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings

# Create SQLAlchemy engine with appropriate settings for SQLite vs PostgreSQL
if settings.database_url.startswith('sqlite'):
    # SQLite doesn't support pool settings
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        echo=settings.is_development
    )
else:
    # PostgreSQL with connection pooling
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.is_development
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use in FastAPI endpoints with Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()