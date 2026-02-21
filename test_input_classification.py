"""
Batch Test Suite for Input Classification
Validates all edge cases to prevent hallucination and ensure predictable behavior
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.agent_orchestrator import agent_orchestrator
from utils.input_classifier import input_classifier
from colorama import init, Fore, Style

init(autoreset=True)


class TestResults:
    """Track test outcomes"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self):
        self.passed += 1
        print(f"{Fore.GREEN}[PASS]{Style.RESET_ALL}")
    
    def add_fail(self, test_name: str, expected: str, actual: str, reason: str = ""):
        self.failed += 1
        self.errors.append({
            'test': test_name,
            'expected': expected,
            'actual': actual,
            'reason': reason
        })
        print(f"{Fore.RED}[FAIL]{Style.RESET_ALL}")
        print(f"  Expected: {expected}")
        print(f"  Got: {actual}")
        if reason:
            print(f"  Reason: {reason}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*70}")
        print(f"TEST SUMMARY")
        print(f"{'='*70}")
        print(f"Total Tests: {total}")
        print(f"{Fore.GREEN}Passed: {self.passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {self.failed}{Style.RESET_ALL}")
        print(f"Success Rate: {(self.passed/total*100) if total > 0 else 0:.1f}%")
        
        if self.errors:
            print(f"\n{Fore.RED}FAILED TESTS:{Style.RESET_ALL}")
            for i, error in enumerate(self.errors, 1):
                print(f"\n{i}. {error['test']}")
                print(f"   Expected: {error['expected']}")
                print(f"   Got: {error['actual']}")
                if error['reason']:
                    print(f"   Reason: {error['reason']}")
        
        return self.failed == 0


def test_classification(test_name: str, input_text: str, expected_category: str, 
                        expected_attributes: dict, results: TestResults):
    """
    Test a single input classification case
    
    Args:
        test_name: Descriptive name of test
        input_text: User input to classify
        expected_category: Expected classification category
        expected_attributes: Dict of attributes to verify in result
        results: TestResults object to track outcomes
    """
    print(f"\n{Fore.CYAN}Testing: {test_name}{Style.RESET_ALL}")
    print(f"Input: '{input_text}'")
    
    try:
        # Classify the input
        category, reason, prompts = input_classifier.classify_input(input_text)
        
        # Check category
        if category != expected_category:
            results.add_fail(
                test_name,
                f"Category: {expected_category}",
                f"Category: {category}",
                f"Classification reason: {reason}"
            )
            return
        
        # Verify expected attributes
        all_passed = True
        
        if 'has_clarification' in expected_attributes:
            expected_prompts = expected_attributes['has_clarification']
            has_prompts = len(prompts) > 0
            if has_prompts != expected_prompts:
                results.add_fail(
                    test_name,
                    f"Has clarification: {expected_prompts}",
                    f"Has clarification: {has_prompts}",
                    f"Prompts: {prompts}"
                )
                return
        
        if 'min_prompts' in expected_attributes:
            min_prompts = expected_attributes['min_prompts']
            if len(prompts) < min_prompts:
                results.add_fail(
                    test_name,
                    f"At least {min_prompts} prompts",
                    f"{len(prompts)} prompts",
                    f"Prompts: {prompts}"
                )
                return
        
        results.add_pass()
        print(f"Category: {category}")
        print(f"Reason: {reason}")
        if prompts:
            print(f"Clarification prompts: {len(prompts)}")
            for prompt in prompts:
                print(f"  - {prompt}")
        
    except Exception as e:
        results.add_fail(test_name, expected_category, "EXCEPTION", str(e))


def test_orchestrator_response(test_name: str, input_text: str, expected_response_type: str,
                                expected_keys: list, results: TestResults):
    """
    Test full orchestrator response for different input types
    
    Args:
        test_name: Descriptive name of test
        input_text: User input to process
        expected_response_type: Expected response structure (category/assessment)
        expected_keys: List of keys that must be present in response
        results: TestResults object to track outcomes
    """
    print(f"\n{Fore.CYAN}Testing: {test_name}{Style.RESET_ALL}")
    print(f"Input: '{input_text}'")
    
    try:
        # Process through orchestrator
        result = agent_orchestrator.assess_user_input(input_text, session_id="test_session")
        
        # Check for expected keys
        missing_keys = [key for key in expected_keys if key not in result]
        if missing_keys:
            results.add_fail(
                test_name,
                f"Keys: {expected_keys}",
                f"Missing: {missing_keys}",
                f"Result keys: {list(result.keys())}"
            )
            return
        
        # Verify response type
        if expected_response_type == "category_response":
            if "category" not in result:
                results.add_fail(
                    test_name,
                    "Category-based response",
                    "Assessment response",
                    f"Result: {result}"
                )
                return
        elif expected_response_type == "assessment":
            if "symptoms_identified" not in result and "emergency_flag" not in result:
                results.add_fail(
                    test_name,
                    "Medical assessment",
                    "Category response",
                    f"Result: {result}"
                )
                return
        
        results.add_pass()
        print(f"Response type: {expected_response_type}")
        print(f"Keys present: {list(result.keys())[:5]}...")
        if "category" in result:
            print(f"Category: {result['category']}")
        if "emergency_flag" in result:
            print(f"Emergency: {result['emergency_flag']}, Urgency: {result.get('urgency_level')}")
        
    except Exception as e:
        results.add_fail(test_name, expected_response_type, "EXCEPTION", str(e))


def run_all_tests():
    """Run comprehensive test suite"""
    results = TestResults()
    
    print(f"{Fore.YELLOW}{'='*70}")
    print(f"BATCH TEST SUITE - INPUT CLASSIFICATION")
    print(f"{'='*70}{Style.RESET_ALL}")
    print(f"Testing all edge cases to prevent hallucination\n")
    
    # ============================================================
    # CATEGORY 1: IRRELEVANT (Non-medical inputs)
    # ============================================================
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"CATEGORY 1: IRRELEVANT INPUTS")
    print(f"{'='*70}{Style.RESET_ALL}")
    
    test_classification(
        "Greeting - Simple Hi",
        "hi",
        "IRRELEVANT",
        {'has_clarification': True, 'min_prompts': 1},
        results
    )
    
    test_classification(
        "Greeting - Hello",
        "hello there",
        "IRRELEVANT",
        {'has_clarification': True},
        results
    )
    
    test_classification(
        "Farewell",
        "goodbye",
        "IRRELEVANT",
        {'has_clarification': True},
        results
    )
    
    test_classification(
        "Social - Thank You",
        "thanks!",
        "IRRELEVANT",
        {'has_clarification': True},
        results
    )
    
    test_classification(
        "Social - Have a Good Day",
        "have a good day",
        "IRRELEVANT",
        {'has_clarification': True},
        results
    )
    
    test_classification(
        "Empty Input",
        "",
        "IRRELEVANT",
        {'has_clarification': True},
        results
    )
    
    # ============================================================
    # CATEGORY 2: INSUFFICIENT_INFO (Vague medical inputs)
    # ============================================================
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"CATEGORY 2: INSUFFICIENT INFORMATION")
    print(f"{'='*70}{Style.RESET_ALL}")
    
    test_classification(
        "Vague - Single Word 'Pain'",
        "pain",
        "INSUFFICIENT_INFO",
        {'has_clarification': True, 'min_prompts': 2},
        results
    )
    
    test_classification(
        "Vague - 'I feel sick'",
        "i feel sick",
        "INSUFFICIENT_INFO",
        {'has_clarification': True},
        results
    )
    
    test_classification(
        "Vague - 'Not feeling well'",
        "not feeling well",
        "INSUFFICIENT_INFO",
        {'has_clarification': True},
        results
    )
    
    test_classification(
        "Vague - 'Something hurts'",
        "something hurts",
        "INSUFFICIENT_INFO",
        {'has_clarification': True},
        results
    )
    
    test_classification(
        "Minimal Detail - 'Headache'",
        "headache",
        "INSUFFICIENT_INFO",
        {'has_clarification': True, 'min_prompts': 3},
        results
    )
    
    # ============================================================
    # CATEGORY 3: EMERGENCY (Immediate triage)
    # ============================================================
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"CATEGORY 3: EMERGENCY INPUTS")
    print(f"{'='*70}{Style.RESET_ALL}")
    
    test_classification(
        "Emergency - Chest Pain",
        "severe chest pain",
        "EMERGENCY",
        {'has_clarification': False},  # No clarification - immediate triage
        results
    )
    
    test_classification(
        "Emergency - Can't Breathe",
        "I can't breathe",
        "EMERGENCY",
        {'has_clarification': False},
        results
    )
    
    test_classification(
        "Emergency - Stroke Symptoms",
        "my face is drooping and arm feels weak",
        "EMERGENCY",
        {'has_clarification': False},
        results
    )
    
    test_classification(
        "Emergency - Severe Bleeding",
        "severe bleeding won't stop",
        "EMERGENCY",
        {'has_clarification': False},
        results
    )
    
    test_classification(
        "Emergency - Suicidal Ideation",
        "I want to die",
        "EMERGENCY",
        {'has_clarification': False},
        results
    )
    
    # ============================================================
    # CATEGORY 4: VALID_MEDICAL (Actionable symptoms)
    # ============================================================
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"CATEGORY 4: VALID MEDICAL INPUTS")
    print(f"{'='*70}{Style.RESET_ALL}")
    
    test_classification(
        "Valid - Detailed Headache",
        "I've had a headache for 3 days, moderate pain on right side",
        "VALID_MEDICAL",
        {'has_clarification': False},
        results
    )
    
    test_classification(
        "Valid - Fever with Duration",
        "fever since yesterday, around 101F with body aches",
        "VALID_MEDICAL",
        {'has_clarification': False},
        results
    )
    
    test_classification(
        "Valid - Multiple Symptoms",
        "cough, runny nose, and sore throat for 5 days",
        "VALID_MEDICAL",
        {'has_clarification': False},
        results
    )
    
    test_classification(
        "Valid - Back Pain with Context",
        "lower back pain started after lifting heavy box, sharp pain when bending",
        "VALID_MEDICAL",
        {'has_clarification': False},
        results
    )
    
    test_classification(
        "Valid - Skin Issue",
        "itchy rash on arms appeared 2 days ago, red and swollen",
        "VALID_MEDICAL",
        {'has_clarification': False},
        results
    )
    
    # ============================================================
    # ORCHESTRATOR INTEGRATION TESTS
    # ============================================================
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"ORCHESTRATOR INTEGRATION TESTS")
    print(f"{'='*70}{Style.RESET_ALL}")
    
    test_orchestrator_response(
        "Orchestrator - Irrelevant Input",
        "hello",
        "category_response",
        ["category", "message", "session_id", "user_input"],
        results
    )
    
    test_orchestrator_response(
        "Orchestrator - Insufficient Info",
        "pain",
        "category_response",
        ["category", "message", "clarifying_questions", "session_id"],
        results
    )
    
    test_orchestrator_response(
        "Orchestrator - Valid Medical (Mock Mode)",
        "headache for 3 days with nausea",
        "assessment",
        ["symptoms_identified", "urgency_level", "recommended_specialty", "session_id"],
        results
    )
    
    # Print final summary
    success = results.summary()
    
    if success:
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"[SUCCESS] ALL TESTS PASSED - System is behaving predictably")
        print(f"{'='*70}{Style.RESET_ALL}")
        return 0
    else:
        print(f"\n{Fore.RED}{'='*70}")
        print(f"[FAILED] SOME TESTS FAILED - Review and fix issues")
        print(f"{'='*70}{Style.RESET_ALL}")
        return 1


if __name__ == "__main__":
    # Install colorama if not present
    try:
        import colorama
    except ImportError:
        print("Installing colorama for colored output...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
        import colorama
        colorama.init(autoreset=True)
    
    exit_code = run_all_tests()
    sys.exit(exit_code)
