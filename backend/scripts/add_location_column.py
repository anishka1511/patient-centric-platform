"""
Database Migration Script - Add extra_data column to messages table
Run this if you have an existing database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from backend.config.database import engine
from backend.config.logging_config import logger


def add_extra_data_column():
    """Add extra_data JSON column to messages table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text(
                "SELECT COUNT(*) FROM pragma_table_info('messages') WHERE name='extra_data'"
            ))
            column_exists = result.scalar() > 0
            
            if column_exists:
                logger.info("✓ extra_data column already exists")
                print("✓ extra_data column already exists in messages table")
            else:
                # Add the column
                conn.execute(text(
                    "ALTER TABLE messages ADD COLUMN extra_data TEXT"
                ))
                conn.commit()
                logger.info("✓ Added extra_data column to messages table")
                print("✓ Successfully added extra_data column to messages table")
                
    except Exception as e:
        logger.error(f"Error adding extra_data column: {e}")
        print(f"✗ Error: {e}")
        print("\nIf the error persists, consider:")
        print("1. Backing up your database")
        print("2. Deleting healthcare_agent.db")
        print("3. Restarting the server (it will recreate with the new schema)")
        sys.exit(1)


if __name__ == "__main__":
    print("="*70)
    print("DATABASE MIGRATION: Adding location data support")
    print("="*70)
    print("\nThis will add an 'extra_data' column to store location and other data\n")
    
    add_extra_data_column()
    
    print("\n" + "="*70)
    print("Migration complete!")
    print("="*70)
    print("\nYou can now include location in your API requests:")
    print('''
    {
      "message": "I have chest pain",
      "location": {
        "city": "New York",
        "state": "NY",
        "latitude": 40.7128,
        "longitude": -74.0060
      }
    }
    ''')
