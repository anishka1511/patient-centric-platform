"""
Test OpenAI API connection and configuration
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings
from config.logging_config import logger
from openai import OpenAI

def test_openai_connection():
    """Test if OpenAI API key is valid and working"""
    
    print("=" * 60)
    print("🧪 Testing OpenAI Configuration")
    print("=" * 60)
    
    # Check if API key is set
    print(f"\n1. API Key Check:")
    if settings.openai_api_key == "sk-your-actual-openai-key-here":
        print("   ❌ API key not configured!")
        print("   Please update OPENAI_API_KEY in .env file")
        return False
    
    if not settings.openai_api_key.startswith("sk-"):
        print("   ❌ Invalid API key format!")
        print("   OpenAI keys should start with 'sk-'")
        return False
    
    key_display = settings.openai_api_key[:10] + "..." + settings.openai_api_key[-4:]
    print(f"   ✓ API key found: {key_display}")
    print(f"   ✓ Model: {settings.openai_model}")
    
    # Test API connection
    print(f"\n2. Testing API Connection:")
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        
        logger.info("Making test API call to OpenAI...")
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello' if you can read this."}
            ],
            max_tokens=10,
            temperature=0.3
        )
        
        message = response.choices[0].message.content
        print(f"   ✓ Connection successful!")
        print(f"   ✓ Response: {message}")
        print(f"   ✓ Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        logger.error(f"OpenAI API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n")
    success = test_openai_connection()
    print("\n" + "=" * 60)
    
    if success:
        print("✅ OpenAI configuration is working correctly!")
        print("=" * 60)
        print("\nYou're ready to proceed to Step 4! 🚀")
    else:
        print("❌ OpenAI configuration failed!")
        print("=" * 60)
        print("\nPlease check your API key and try again.")
        sys.exit(1)
