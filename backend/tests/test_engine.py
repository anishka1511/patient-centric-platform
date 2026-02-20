import sys
from pathlib import Path
from pprint import pprint

# Add parent directory to path to import from data_loader
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_loader import generate_recommendation_response


def test_recommendation_engine():
    """
    Test the recommendation engine with sample input.
    """
    sample_input = {
        "specialty": "Dentist",
        "location": "Baner",
        "top_k": 3
    }
    
    print("=" * 60)
    print("Testing generate_recommendation_response")
    print("=" * 60)
    print("\nInput:")
    pprint(sample_input)
    
    try:
        result = generate_recommendation_response(sample_input)
        print("\nResult:")
        pprint(result)
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure 'data/doctors_cleaned.csv' exists.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_recommendation_engine()
