#!/usr/bin/env python3
"""
Interactive test script for the healthcare recommendation system.
Allows testing with user-provided severity, location, and specialty inputs.
"""

import json
from data_loader import generate_recommendation_response


def format_response(response):
    """Pretty-print the recommendation response."""
    print("\n" + "="*80)
    print("RECOMMENDATION RESULT")
    print("="*80 + "\n")
    print(json.dumps(response, indent=2))
    print("\n" + "="*80 + "\n")


def get_severity():
    """Prompt user for severity level."""
    while True:
        severity = input("\nEnter severity level (low/medium/high): ").strip().lower()
        if severity in ["low", "medium", "high"]:
            return severity
        print("❌ Invalid severity. Must be 'low', 'medium', or 'high'.")


def get_location():
    """Prompt user for location."""
    while True:
        location = input("\nEnter location (e.g., baner, wakad, kharadi): ").strip().lower()
        if location:
            return location
        print("❌ Location cannot be empty.")


def get_specialty():
    """Prompt user for specialty."""
    while True:
        specialty = input("\nEnter specialty/doctor type (e.g., cardiologist, dentist, general_physician): ").strip().lower()
        if specialty:
            return specialty
        print("❌ Specialty cannot be empty.")


def main():
    """Main interactive test loop."""
    print("\n" + "="*80)
    print("HEALTHCARE RECOMMENDATION SYSTEM - INTERACTIVE TEST")
    print("="*80)
    
    while True:
        try:
            # Get user inputs
            severity = get_severity()
            location = get_location()
            specialty = get_specialty()
            
            # Prepare input data
            input_data = {
                "severity": severity,
                "location": location,
                "specialty": specialty
            }
            
            print(f"\n📋 Processing request...")
            print(f"   Severity: {severity}")
            print(f"   Location: {location}")
            print(f"   Specialty: {specialty}")
            
            # Get recommendation
            response = generate_recommendation_response(input_data)
            
            # Display result
            format_response(response)
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.\n")
        
        # Ask if user wants to test again
        again = input("\nTest another query? (yes/no): ").strip().lower()
        if again not in ["yes", "y"]:
            print("\nThank you for testing! Goodbye. 👋\n")
            break


if __name__ == "__main__":
    main()
