"""
Database Schema Fix - Add extra_data column to messages table
Run this once to update existing database without losing data
"""
import sqlite3
from pathlib import Path
import sys

def fix_schema(silent=False):
    """
    Add extra_data column to messages table
    
    Args:
        silent: If True, don't print output (for use in main.py)
    """
    db_path = Path(__file__).parent / "healthcare_agent.db"
    
    def log(msg):
        if not silent:
            print(msg)
    
    if not db_path.exists():
        log(f"ℹ️  Database not found - will be created with correct schema on first run")
        return True
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'extra_data' not in columns:
            log("🔧 Adding extra_data column to messages table...")
            cursor.execute("ALTER TABLE messages ADD COLUMN extra_data TEXT")
            conn.commit()
            log("✅ Column added successfully!")
        else:
            log("✅ extra_data column already exists")
        
        conn.close()
        return True
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            log("✅ Column already exists")
            return True
        log(f"❌ Schema fix failed: {e}")
        return False
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE SCHEMA FIX")
    print("=" * 60)
    if fix_schema(silent=False):
        print("\n✅ Database updated! You can now run:")
        print("   python test_interactive.py")
        print("   python main.py")
    else:
        print("\n❌ Fix failed. Try deleting database and starting fresh:")
        print("   rm healthcare_agent.db  (or: del healthcare_agent.db on Windows)")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE SCHEMA FIX")
    print("=" * 60)
    if fix_schema():
        print("\n✅ Database updated! You can now run:")
        print("   python test_interactive.py")
        print("   python main.py")
    else:
        print("\n❌ Fix failed. Try deleting database and starting fresh:")
        print("   rm healthcare_agent.db  (or: del healthcare_agent.db on Windows)")
    print("=" * 60)
