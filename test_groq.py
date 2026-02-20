"""
Test Groq AI Connection
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from config.settings import settings
from config.logging_config import logger
from openai import OpenAI

def test_groq_connection():
    """Test if Groq AI is working"""
    
    print("=" * 70)
    print("🧪 Testing Groq AI Connection")
    print("=" * 70)
    
    # Check configuration
    print(f"\n1. Configuration Check:")
    print(f"   • Provider: {settings.llm_provider}")
    print(f"   • Model: {settings.openai_model}")
    print(f"   • Base URL: {getattr(settings, 'groq_base_url', 'Not set')}")
    
    if settings.groq_api_key == "your-groq-api-key-here":
        print("\n❌ ERROR: Groq API key not configured!")
        print("\nPlease update your .env file:")
        print("   GROQ_API_KEY=gsk-your-actual-groq-key")
        return False
    
    key_display = settings.groq_api_key[:10] + "..." + settings.groq_api_key[-6:]
    print(f"   • API Key: {key_display}")
    
    # Test connection
    print(f"\n2. Testing Groq API:")
    try:
        client = OpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url
        )
        
        print("   • Sending test request...")
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from Groq!' if you can read this."}
            ],
            max_tokens=20,
            temperature=0.3
        )
        
        message = response.choices[0].message.content
        print(f"   ✅ Connection successful!")
        print(f"   ✅ Response: {message}")
        print(f"   ✅ Tokens used: {response.usage.total_tokens}")
        
        print("\n" + "=" * 70)
        print("✅ Groq AI is ready to use!")
        print("=" * 70)
        print("\n💡 Groq advantages:")
        print("   • Super fast inference (~100-500 tokens/sec)")
        print("   • Generous free tier")
        print("   • Great for structured outputs")
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed!")
        print(f"   Error: {str(e)}")
        print("\n" + "=" * 70)
        print("❌ Groq AI connection failed!")
        print("=" * 70)
        print("\nTroubleshooting:")
        print("1. Check your API key at https://console.groq.com/")
        print("2. Make sure you have quota available")
        print("3. Verify the API key is correctly set in .env")
        return False

if __name__ == "__main__":
    success = test_groq_connection()
    if success:
        print("\n🚀 Ready to test with real inputs!")
        print("   Run: python test_complete_system.py")
    sys.exit(0 if success else 1)
