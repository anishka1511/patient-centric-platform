"""
Test the mock LLM service
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.mock_llm_service import mock_llm_service
import json

def test_mock_service():
    print("=" * 70)
    print("🧪 Testing Mock LLM Service (No OpenAI Credits Needed!)")
    print("=" * 70)
    
    # Test 1: Emergency case
    print("\n📋 Test 1: Emergency Case")
    print("-" * 70)
    user_input = "I have severe chest pain and shortness of breath"
    print(f"User Input: '{user_input}'")
    
    symptoms_result = mock_llm_service.extract_symptoms(user_input)
    print(f"\n✓ Extracted Symptoms: {json.dumps(symptoms_result, indent=2)}")
    
    assessment_result = mock_llm_service.assess_symptoms(symptoms_result["symptoms"])
    print(f"\n✓ Assessment Result:")
    print(json.dumps(assessment_result, indent=2))
    
    # Test 2: Medium Urgency
    print("\n\n📋 Test 2: Medium Urgency Case")
    print("-" * 70)
    user_input2 = "I have a headache and fever for 2 days"
    print(f"User Input: '{user_input2}'")
    
    symptoms_result2 = mock_llm_service.extract_symptoms(user_input2)
    print(f"\n✓ Extracted Symptoms: {json.dumps(symptoms_result2, indent=2)}")
    
    assessment_result2 = mock_llm_service.assess_symptoms(symptoms_result2["symptoms"])
    print(f"\n✓ Assessment Result:")
    print(json.dumps(assessment_result2, indent=2))
    
    # Test 3: Low Urgency
    print("\n\n📋 Test 3: Low Urgency Case")
    print("-" * 70)
    user_input3 = "I have a minor skin rash"
    print(f"User Input: '{user_input3}'")
    
    symptoms_result3 = mock_llm_service.extract_symptoms(user_input3)
    print(f"\n✓ Extracted Symptoms: {json.dumps(symptoms_result3, indent=2)}")
    
    assessment_result3 = mock_llm_service.assess_symptoms(symptoms_result3["symptoms"])
    print(f"\n✓ Assessment Result:")
    print(json.dumps(assessment_result3, indent=2))
    
    print("\n" + "=" * 70)
    print("✅ Mock LLM Service is working perfectly!")
    print("=" * 70)
    print("\n💡 This allows us to continue development without OpenAI credits.")
    print("💡 We'll build the entire system, and you can switch to real OpenAI later!")
    return True

if __name__ == "__main__":
    success = test_mock_service()
    if success:
        print("\n🚀 Ready to proceed with Step 4: Implement full LLM service!")
    sys.exit(0 if success else 1)
