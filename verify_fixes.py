"""Direct test of input classifier fixes"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.input_classifier import input_classifier

# Test the three failing cases
print("Testing fixes...\n")

test_cases = [
    ("pain", "INSUFFICIENT_INFO"),
    ("i feel sick", "INSUFFICIENT_INFO"),
    ("my face is drooping and arm feels weak", "EMERGENCY"),
]

all_pass = True
for input_text, expected in test_cases:
    category, reason, prompts = input_classifier.classify_input(input_text)
    passed = (category == expected)
    status = "✓ PASS" if passed else "✗ FAIL"
    
    print(f"{status}: '{input_text}'")
    print(f"  Expected: {expected}, Got: {category}")
    if not passed:
        print(f"  Reason: {reason}")
        all_pass = False
    print()

if all_pass:
    print("✓ All critical fixes working!")
else:
    print("✗ Some tests still failing")
