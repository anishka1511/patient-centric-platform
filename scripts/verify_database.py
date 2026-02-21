"""
Verify database tables were created correctly
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import engine
from sqlalchemy import inspect

def verify_database():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("📊 Database Tables:")
    print("=" * 50)
    
    for table_name in tables:
        print(f"\n✓ Table: {table_name}")
        columns = inspector.get_columns(table_name)
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    
    print("\n" + "=" * 50)
    print(f"✅ Total tables: {len(tables)}")
    return len(tables) == 3

if __name__ == "__main__":
    success = verify_database()
    if success:
        print("\n🎉 Database verification passed!")
    else:
        print("\n❌ Database verification failed!")
        sys.exit(1)
