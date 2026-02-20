"""
Interactive Test - Try Your Own Inputs
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.agent_orchestrator import agent_orchestrator
import json

print("="*70)
print("INTERACTIVE SYMPTOM ASSESSMENT TEST")
print("="*70)
print("Test different types of input:")
print("  - Greetings: 'hi', 'hello'")
print("  - Vague: 'pain', 'not feeling well'")
print("  - Emergency: 'chest pain', 'can't breathe'")
print("  - Valid: 'headache for 3 days', 'fever with cough'")
print("\nType 'quit' to exit\n")
print("="*70)

while True:
    try:
        user_input = input("\nYour input: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nExiting. Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Process through orchestrator
        result = agent_orchestrator.assess_user_input(user_input, session_id="test_session")
        
        print("\n" + "-"*70)
        print("RESULT:")
        print("-"*70)
        
        # Display based on response type
        if "category" in result:
            # Category response (IRRELEVANT or INSUFFICIENT_INFO)
            print(f"Category: {result['category']}")
            print(f"Message: {result.get('message', '')}")
            
            if "clarifying_questions" in result:
                print("\nClarifying Questions:")
                for q in result['clarifying_questions']:
                    print(f"  - {q}")
            
            if "suggestions" in result and result['suggestions']:
                print("\nSuggestions:")
                for s in result['suggestions']:
                    print(f"  - {s}")
        
        else:
            # Medical assessment response
            print(f"Symptoms: {', '.join(result.get('symptoms_identified', []))}")
            print(f"Urgency: {result.get('urgency_level', 'unknown').upper()}")
            print(f"Emergency: {'YES' if result.get('emergency_flag') else 'NO'}")
            print(f"Specialty: {result.get('recommended_specialty', 'N/A')}")
            print(f"Care Setting: {result.get('care_setting', 'N/A')}")
            
            if result.get('reasoning'):
                print(f"\nReasoning: {result['reasoning']}")
            
            if result.get('safety_advice'):
                print(f"\n⚠️  SAFETY ADVICE: {result['safety_advice']}")
        
        print("-"*70)
        
    except KeyboardInterrupt:
        print("\n\nExiting. Goodbye!")
        break
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
