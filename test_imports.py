"""
Simple test to verify models can be imported
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Testing imports...")

try:
    print("1. Importing settings...")
    from config.settings import settings
    print(f"   ✓ Settings loaded: {settings.app_name}")
    
    print("2. Importing database...")
    from config.database import Base, engine
    print(f"   ✓ Database loaded: {settings.database_url}")
    
    print("3. Importing Conversation model...")
    from models.conversation import Conversation
    print(f"   ✓ Conversation model loaded")
    
    print("4. Importing Message model...")
    from models.message import Message, MessageRole
    print(f"   ✓ Message model loaded")
    
    print("5. Importing Assessment model...")
    from models.assessment import Assessment, UrgencyLevel, CareSetting
    print(f"   ✓ Assessment model loaded")
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
