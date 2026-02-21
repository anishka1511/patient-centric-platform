"""
Quick Interactive Test Script
Test input classification with simple examples
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.input_classifier import input_classifier

# Test cases
test_cases = [
    ("hi", "IRRELEVANT"),
    ("hello there", "IRRELEVANT"),
    ("have a good day", "IRRELEVANT"),
    ("pain", "INSUFFICIENT_INFO"),
    ("i feel sick", "INSUFFICIENT_INFO"),
    ("severe chest pain", "EMERGENCY"),
    ("I can't breathe", "EMERGENCY"),
    ("my face is drooping and arm feels weak", "EMERGENCY"),
    ("headache for 3 days with nausea", "VALID_MEDICAL"),
    ("fever since yesterday around 101F", "VALID_MEDICAL"),
]

print("="*70)
print("QUICK INPUT CLASSIFICATION TEST")
print("="*70)

passed = 0
failed = 0

for input_text, expected in test_cases:
    category, reason, prompts = input_classifier.classify_input(input_text)
    status = "[PASS]" if category == expected else "[FAIL]"
    
    if category == expected:
        passed += 1
        print(f"\n{status} '{input_text}'")
        print(f"  Category: {category}")
    else:
        failed += 1
        print(f"\n{status} '{input_text}'")
        print(f"  Expected: {expected}")
        print(f"  Got: {category}")
        print(f"  Reason: {reason}")

print(f"\n{'='*70}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*70}")

if failed == 0:
    print("\n[SUCCESS] All tests passed!")
else:
    print(f"\n[FAILED] {failed} test(s) failed")

sys.exit(0 if failed == 0 else 1)
