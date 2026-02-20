"""
Test LLM-based Input Classification
Tests the new 2-API-call architecture with LLM classification
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.agent_orchestrator import agent_orchestrator

# Test cases with dermatology terms and other edge cases
test_cases = [
    # IRRELEVANT - Greetings and social
    ("hi", "IRRELEVANT", "greeting"),
    ("hello there", "IRRELEVANT", "greeting"),
    ("thanks!", "IRRELEVANT", "social"),
    ("have a good day", "IRRELEVANT", "farewell"),
    
    # INSUFFICIENT_INFO - Vague symptoms
    ("pain", "INSUFFICIENT_INFO", "vague location"),
    ("i feel sick", "INSUFFICIENT_INFO", "too vague"),
    ("not feeling well", "INSUFFICIENT_INFO", "no specifics"),
    
    # EMERGENCY - Life-threatening symptoms
    ("severe chest pain", "EMERGENCY", "cardiac"),
    ("I can't breathe", "EMERGENCY", "respiratory"),
    ("my face is drooping and arm feels weak", "EMERGENCY", "stroke"),
    
    # VALID_MEDICAL - Specific symptom descriptions
    ("headache for 3 days with nausea", "VALID_MEDICAL", "specific with duration"),
    ("fever since yesterday around 101F", "VALID_MEDICAL", "specific with details"),
    
    # DERMATOLOGY - The new test cases that were failing
    ("cherry angioma", "VALID_MEDICAL", "dermatology term"),
    ("face pimple", "VALID_MEDICAL", "dermatology symptom"),
    ("face bump of red colour", "VALID_MEDICAL", "dermatology with color"),
    ("skin rash on arm", "VALID_MEDICAL", "dermatology location"),
]

print("="*70)
print("LLM-BASED INPUT CLASSIFICATION TEST (2 API CALLS ARCHITECTURE)")
print("="*70)
print("\nTesting classify_input() method that combines classification + extraction")
print("This should handle dermatology terms and all medical specialties automatically\n")

passed = 0
failed = 0
errors = []

for input_text, expected, note in test_cases:
    try:
        result = agent_orchestrator.assess_user_input(input_text, session_id="test_llm")
        
        # Determine actual category from result
        if "category" in result:
            actual = result["category"]
        elif result.get("emergency_flag"):
            actual = "EMERGENCY"
        else:
            actual = "VALID_MEDICAL"
        
        status = "[PASS]" if actual == expected else "[FAIL]"
        
        if actual == expected:
            passed += 1
            print(f"\n{status} '{input_text}'")
            print(f"  Category: {actual} ({note})")
        else:
            failed += 1
            errors.append({
                'input': input_text,
                'expected': expected,
                'actual': actual,
                'note': note
            })
            print(f"\n{status} '{input_text}'")
            print(f"  Expected: {expected} ({note})")
            print(f"  Got: {actual}")
            if "symptoms_identified" in result:
                print(f"  Symptoms extracted: {result['symptoms_identified']}")
            if "message" in result:
                print(f"  Message: {result['message']}")
                
    except Exception as e:
        failed += 1
        errors.append({
            'input': input_text,
            'expected': expected,
            'actual': f"ERROR: {str(e)}",
            'note': note
        })
        print(f"\n[ERROR] '{input_text}'")
        print(f"  Exception: {str(e)}")

print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}")
print(f"Total: {len(test_cases)} tests")
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if errors:
    print(f"\n{'='*70}")
    print(f"FAILURES")
    print(f"{'='*70}")
    for err in errors:
        print(f"\nInput: '{err['input']}'")
        print(f"  Expected: {err['expected']} ({err['note']})")
        print(f"  Got: {err['actual']}")

print(f"\n{'='*70}")
if failed == 0:
    print("[SUCCESS] All tests passed! LLM classification working correctly.")
    print("Dermatology terms and all medical specialties handled automatically.")
else:
    print(f"[FAILED] {failed} test(s) failed")
    print("Note: LLM results may vary. Review failures to assess severity.")
print(f"{'='*70}")

sys.exit(0 if failed == 0 else 1)
