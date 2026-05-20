"""
Quick migration to add extra_data column to messages table
"""
import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).parent / "healthcare_agent.db"

print(f"Updating database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("PRAGMA table_info(messages)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'extra_data' in columns:
        print("✓ extra_data column already exists")
    else:
        # Add the column
        print("Adding extra_data column...")
        cursor.execute("ALTER TABLE messages ADD COLUMN extra_data TEXT")
        conn.commit()
        print("✓ extra_data column added successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nMigration complete. You can now run test_interactive.py")
