import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import Base, engine
from config.logging_config import logger
# Import models directly to avoid circular import issues
from models.conversation import Conversation
from models.message import Message
from models.assessment import Assessment


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