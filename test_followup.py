"""Test follow-up responses"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.input_classifier import input_classifier

# Test the problematic case
test_cases = [
    "back pain",
    "upper back near the spine, had since a month, moderate, no",
    "left side, started 2 weeks ago, sharp",
    "head, for about 5 days, severe headache",
    "chest area, mild discomfort, few hours"
]

for test in test_cases:
    category, reason, prompts = input_classifier.classify_input(test)
    print(f"\nInput: '{test}'")
    print(f"Category: {category}")
    print(f"Reason: {reason}")
    if prompts:
        print(f"Prompts: {len(prompts)}")
