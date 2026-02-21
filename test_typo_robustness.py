"""
Typo Robustness Test - Emergency Detection with Fuzzy Matching
Tests that common typos and misspellings are caught
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.input_classifier import input_classifier

print("="*70)
print("🔍 TYPO ROBUSTNESS TEST - Emergency Detection with Fuzzy Matching")
print("="*70)
print("Testing that misspellings are caught\n")

# Emergency phrases WITH typos (real-world examples)
typo_cases = [
    # Breathing typos
    ("brathlessness", "EMERGENCY", "breathlessness"),
    ("cant breth", "EMERGENCY", "can't breathe"),
    ("cant breath", "EMERGENCY", "can't breathe"),
    ("brething difficulty", "EMERGENCY", "breathing difficulty"),
    ("shortnes of breath", "EMERGENCY", "shortness of breath"),
    ("chocking", "EMERGENCY", "choking"),
    
    # Chest/cardiac typos
    ("cheast pain", "EMERGENCY", "chest pain"),
    ("chest pian", "EMERGENCY", "chest pain"),
    ("hart attack", "EMERGENCY", "heart attack"),
    ("heart atack", "EMERGENCY", "heart attack"),
    
    # Stroke typos
    ("fase drooping", "EMERGENCY", "face drooping"),
    ("face dropin", "EMERGENCY", "face drooping"),
    ("slured speech", "EMERGENCY", "slurred speech"),
    
    # Consciousness typos
    ("passed owt", "EMERGENCY", "passed out"),
    ("unconcsious", "EMERGENCY", "unconscious"),
    ("blacked owt", "EMERGENCY", "blacked out"),
    
    # Other critical typos
    ("sevear bleeding", "EMERGENCY", "severe bleeding"),
    ("seazure", "EMERGENCY", "seizure"),
    ("overdoze", "EMERGENCY", "overdose"),
]

print("Testing typo detection:\n")
passed = 0
failed = 0

for phrase, expected, correct_term in typo_cases:
    category, reason, prompts = input_classifier.classify_input(phrase)
    
    if category == "EMERGENCY":
        passed += 1
        print(f"✅ '{phrase}' → EMERGENCY (corrected from '{correct_term}')")
    else:
        failed += 1
        print(f"❌ MISSED: '{phrase}' → {category} (should detect '{correct_term}')")
        print(f"   Reason: {reason}")

print(f"\n{'='*70}")
print(f"Typo Detection: {passed}/{len(typo_cases)} passed")
print(f"Success Rate: {(passed/len(typo_cases)*100):.1f}%")
print(f"{'='*70}")

# Test that normal symptoms still work
print(f"\n{'='*70}")
print("Regression Test: Normal symptoms still work")
print(f"{'='*70}\n")

normal_cases = [
    ("headache", "VALID_MEDICAL"),
    ("stomach pain", "VALID_MEDICAL"),
    ("back ache", "VALID_MEDICAL"),
]

normal_passed = 0
for phrase, expected in normal_cases:
    category, _, _ = input_classifier.classify_input(phrase)
    if category == expected:
        normal_passed += 1
        print(f"✅ '{phrase}' → {category}")
    else:
        print(f"❌ '{phrase}' → {category} (expected {expected})")

print(f"\n{'='*70}")
if failed == 0 and normal_passed == len(normal_cases):
    print("🏆 TYPO ROBUSTNESS TEST PASSED")
    print("System handles real-world misspellings!")
else:
    print(f"⚠️  Caught {passed}/{len(typo_cases)} typos")
    print("Consider adjusting fuzzy matching threshold")
print(f"{'='*70}")

sys.exit(0 if failed == 0 else 1)
