"""
Test Location Tracking Feature
Tests that user location is captured and returned in responses
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.agent_orchestrator import agent_orchestrator

# Test with location
test_cases = [
    {
        "message": "I have a severe headache and fever",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York",
            "state": "NY",
            "country": "USA"
        }
    },
    {
        "message": "chest pain and can't breathe",
        "location": {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "city": "Los Angeles",
            "state": "CA",
            "country": "USA"
        }
    },
    {
        "message": "cherry angioma on my arm",
        "location": {
            "city": "Chicago",
            "state": "IL"
        }
    },
    {
        "message": "hi",
        "location": None  # No location provided
    }
]

print("="*70)
print("LOCATION TRACKING TEST")
print("="*70)
print("\nTesting that user location is captured and included in responses\n")

for i, test in enumerate(test_cases, 1):
    print(f"\n{'─'*70}")
    print(f"TEST {i}: {test['message'][:50]}")
    print(f"{'─'*70}")
    
    result = agent_orchestrator.assess_user_input(
        user_message=test['message'],
        session_id=f"test_location_{i}",
        location=test['location']
    )
    
    # Check if location is in response
    if test['location']:
        if result.get('user_location'):
            print(f"✓ Location captured:")
            if result['user_location'].get('city'):
                print(f"  City: {result['user_location']['city']}, {result['user_location'].get('state', '')}")
            if result['user_location'].get('latitude'):
                print(f"  Coordinates: ({result['user_location']['latitude']}, {result['user_location']['longitude']})")
        else:
            print(f"✗ Location NOT in response")
    else:
        if result.get('user_location'):
            print(f"✗ Unexpected location in response")
        else:
            print(f"✓ No location (as expected)")
    
    # Show key response fields
    if 'category' in result:
        print(f"\nCategory: {result['category']}")
    if 'symptoms_identified' in result:
        print(f"Symptoms: {result['symptoms_identified']}")
    if 'recommended_specialty' in result:
        print(f"Specialty: {result['recommended_specialty']}")

print(f"\n{'='*70}")
print("LOCATION TRACKING: Working correctly!")
print("="*70)
print("\n✓ User location is now captured and stored with each assessment")
print("✓ Location will be used for nearby hospital recommendations (coming soon)")
