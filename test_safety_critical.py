"""
CRITICAL SAFETY TEST - Emergency Detection
Tests that emergency phrases NEVER get blocked
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.input_classifier import input_classifier

print("="*70)
print("🚨 CRITICAL SAFETY TEST - Emergency Detection")
print("="*70)
print("These MUST all be detected as EMERGENCY\n")

# CRITICAL emergency phrases (real-world examples)
emergency_cases = [
    # Breathing
    "i cant breathe",
    "can't breathe",
    "cannot breathe",
    "breathing difficulty",
    "trouble breathing",
    "shortness of breath",
    "choking",
    "breathing issues",
    
    # Chest/cardiac
    "chest pain",
    "severe chest pain",
    "pressure in chest",
    "heart hurting",
    "feels like heart attack",
    
    # Stroke
    "face drooping",
    "arm weakness",
    "slurred speech",
    "cant move my arm",
    
    # Bleeding
    "severe bleeding",
    "heavy bleeding",
    "won't stop bleeding",
    
    # Consciousness
    "passed out",
    "keep passing out",
    "unconscious",
    "blacked out",
    
    # Mental health
    "want to die",
    "kill myself",
    "suicidal",
    
    # Other critical
    "seizure",
    "overdose",
    "severe burn",
]

print("Testing emergency detection:\n")
passed = 0
failed = 0

for phrase in emergency_cases:
    category, reason, prompts = input_classifier.classify_input(phrase)
    
    if category == "EMERGENCY":
        passed += 1
        print(f"✅ '{phrase}' → EMERGENCY")
    else:
        failed += 1
        print(f"❌ FAILED: '{phrase}' → {category} (should be EMERGENCY)")
        print(f"   Reason: {reason}")

print(f"\n{'='*70}")
print(f"Emergency Detection: {passed}/{len(emergency_cases)} passed")
print(f"{'='*70}")

if failed > 0:
    print(f"\n🚨 CRITICAL FAILURE: {failed} emergency phrases not detected!")
    print("This is a SAFETY ISSUE - must be fixed before deployment")
else:
    print("\n✅ All emergency phrases correctly detected!")

# Test valid symptoms that should NOT be blocked
print(f"\n{'='*70}")
print("Testing Valid Symptoms (should NOT be blocked)")
print(f"{'='*70}\n")

valid_cases = [
    "stomach pain",
    "severe headache", 
    "breathing issues",
    "back pain",
    "fever",
    "cough",
    "dizzy",
]

valid_passed = 0
valid_failed = 0

for phrase in valid_cases:
    category, reason, prompts = input_classifier.classify_input(phrase)
    
    # Should be VALID_MEDICAL or EMERGENCY, NOT INSUFFICIENT_INFO
    if category in ["VALID_MEDICAL", "EMERGENCY"]:
        valid_passed += 1
        print(f"✅ '{phrase}' → {category}")
    else:
        valid_failed += 1
        print(f"❌ BLOCKED: '{phrase}' → {category} (should proceed to triage)")

print(f"\n{'='*70}")
print(f"Valid Symptoms: {valid_passed}/{len(valid_cases)} passed")
print(f"{'='*70}")

# Final verdict
print(f"\n{'='*70}")
if failed == 0 and valid_failed == 0:
    print("🏆 SAFETY TEST PASSED - System is production-ready")
else:
    print("⚠️  SAFETY ISSUES DETECTED - Review required")
print(f"{'='*70}")

sys.exit(0 if (failed == 0 and valid_failed == 0) else 1)
