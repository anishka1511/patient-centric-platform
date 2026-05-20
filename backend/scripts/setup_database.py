import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.config.database import Base, engine
from backend.config.logging_config import logger
# Import models directly to avoid circular import issues
from backend.models.conversation import Conversation
from backend.models.message import Message
from backend.models.assessment import Assessment
from backend.models.review import Review


def init_db():
    """Initialize database - create all tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False


if __name__ == "__main__":
    success = init_db()
    if success:
        print("✅ Database initialized successfully!")
    else:
        print("❌ Database initialization failed!")
        sys.exit(1)
