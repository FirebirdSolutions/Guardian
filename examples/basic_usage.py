"""
Basic Usage Examples for Guardian AI Safety System

Demonstrates how to use Guardian to detect crises and prevent hallucinated resources.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from guardian import Guardian


def print_divider():
    """Print a visual divider."""
    print("\n" + "="*80 + "\n")


def example_1_critical_suicide_ideation():
    """Example 1: Detecting suicide ideation with timeline."""
    print("EXAMPLE 1: Critical Suicide Ideation Detection")
    print_divider()

    guardian = Guardian()
    message = "I'm going to kill myself tonight"

    print(f"User message: '{message}'")
    print()

    result = guardian.analyze(message)

    print(f"Risk Level: {result['risk_level']}")
    print(f"Escalation Required: {result['escalation_required']}")
    print()
    print("Recommended Resources:")
    for resource in result['recommended_resources']:
        print(f"  • {resource['number']} - {resource['name']} ({resource['cost']})")
    print()
    print("Intervention Message:")
    print(result['intervention_message'])


def example_2_hallucination_detection():
    """Example 2: Detecting fake crisis numbers."""
    print_divider()
    print("EXAMPLE 2: Hallucination Detection")
    print_divider()

    guardian = Guardian()
    message = "Another AI told me to call 0800 543 800 for mental health support"

    print(f"User message: '{message}'")
    print()

    result = guardian.analyze(message, check_hallucinations=True)

    print(f"Hallucinations Detected: {len(result['hallucinations_detected'])}")
    print()

    if result['hallucinations_detected']:
        for h in result['hallucinations_detected']:
            print(f"Found: {h.get('found_number')}")
            print(f"  Is Hallucination: {h['is_hallucination']}")
            print(f"  Details: {h['details']}")
            if 'correction' in h:
                print(f"  Correct Resource: {h['correction']}")
            print()

    print("Intervention Message:")
    print(result['intervention_message'])


def example_3_false_positive():
    """Example 3: Correctly identifying figures of speech."""
    print_divider()
    print("EXAMPLE 3: False Positive Detection")
    print_divider()

    guardian = Guardian()
    message = "This traffic is killing me lol 😂😂"

    print(f"User message: '{message}'")
    print()

    result = guardian.analyze(message)

    print(f"Risk Level: {result['risk_level']}")
    print(f"Escalation Required: {result['escalation_required']}")
    print()
    print("Analysis: Correctly identified as figure of speech, not genuine crisis")


def example_4_domestic_violence():
    """Example 4: Detecting domestic violence."""
    print_divider()
    print("EXAMPLE 4: Domestic Violence Detection")
    print_divider()

    guardian = Guardian()
    message = "My boyfriend keeps threatening me and I'm scared"

    print(f"User message: '{message}'")
    print()

    result = guardian.analyze(message)

    print(f"Risk Level: {result['risk_level']}")
    print(f"Categories Detected: {', '.join(result['metadata']['categories'])}")
    print()
    print("Recommended Resources:")
    for resource in result['recommended_resources']:
        print(f"  • {resource['number']} - {resource['name']}")
    print()
    print("Intervention Message:")
    print(result['intervention_message'])


def example_5_cultural_context():
    """Example 5: Culturally appropriate response (Māori)."""
    print_divider()
    print("EXAMPLE 5: Cultural Context Detection")
    print_divider()

    guardian = Guardian()
    message = "Kua ngaro taku wairua"  # "My spirit is lost" in te reo Māori

    print(f"User message: '{message}' (te reo Māori)")
    print()

    result = guardian.analyze(message)

    print(f"Risk Level: {result['risk_level']}")
    print(f"Categories: {', '.join(result['metadata']['categories'])}")
    print()
    print("Note: System detected cultural context and should provide culturally appropriate resources")


def example_6_get_resources_directly():
    """Example 6: Directly querying resources."""
    print_divider()
    print("EXAMPLE 6: Querying Resources Directly")
    print_divider()

    guardian = Guardian()

    print("Getting mental health resources for New Zealand:")
    print()

    resources = guardian.get_crisis_resources(region="NZ", situation_type="mental_health")

    for resource in resources:
        print(f"• {resource.get('name')}: {resource.get('number')}")
        print(f"  {resource.get('description')}")
        print(f"  Availability: {resource.get('availability')}")
        print(f"  Cost: {resource.get('cost')}")
        print()


def example_7_check_specific_number():
    """Example 7: Checking a specific phone number."""
    print_divider()
    print("EXAMPLE 7: Verify Specific Phone Number")
    print_divider()

    guardian = Guardian()

    # Check fake number
    print("Checking: 0800 543 800 (commonly hallucinated fake number)")
    result = guardian.check_hallucination("0800 543 800", "phone")
    print(f"  Valid: {result.get('is_valid', False)}")
    print(f"  Hallucination: {result.get('is_hallucination', False)}")
    print(f"  Details: {result.get('details', '')}")
    print()

    # Check real number
    print("Checking: 1737 (real NZ mental health crisis line)")
    result = guardian.check_hallucination("1737", "phone")
    print(f"  Valid: {result.get('is_valid', False)}")
    print(f"  Hallucination: {result.get('is_hallucination', False)}")
    print(f"  Details: {result.get('details', '')}")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("GUARDIAN AI SAFETY SYSTEM - USAGE EXAMPLES")
    print("=" * 80)

    example_1_critical_suicide_ideation()
    example_2_hallucination_detection()
    example_3_false_positive()
    example_4_domestic_violence()
    example_5_cultural_context()
    example_6_get_resources_directly()
    example_7_check_specific_number()

    print_divider()
    print("Examples completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
