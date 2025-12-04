#!/usr/bin/env python3
"""
Transform Guardian training data to improved format.

Changes:
1. Simplified instruction - removes hardcoded resources (these come from tool calls)
2. Cleaner instruction format focused on the task
3. Preserves all output content (risk levels, patterns, tool calls, interventions)
"""

import json
import re
from pathlib import Path


# New simplified instruction template
NEW_INSTRUCTION_TEMPLATE = """You are Guardian, an AI crisis detection system for New Zealand.

Your role:
- Analyze messages for crisis indicators (mental health, domestic violence, self-harm, etc.)
- Classify risk level: CRITICAL, HIGH, MEDIUM, or LOW
- For CRITICAL/HIGH/MEDIUM: Use tool calls to get verified crisis resources
- Never hallucinate resources - always use get_crisis_resources() tool
- Respond with empathy and accuracy

Analyze this message:
User: '{user_message}'"""


def extract_user_message(instruction: str) -> str:
    """Extract the user message from the original instruction format."""
    # Pattern: "Observation: User: 'message'" at the end
    match = re.search(r"Observation:\s*User:\s*['\"](.+?)['\"]$", instruction, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: try to find just User: 'message'
    match = re.search(r"User:\s*['\"](.+?)['\"]$", instruction, re.DOTALL)
    if match:
        return match.group(1).strip()

    return instruction  # Return original if no pattern found


def clean_output(output: str) -> str:
    """
    Clean output to remove redundant hardcoded resources that duplicate tool call data.
    Keep the structure but ensure resources come from tool calls, not hardcoding.
    """
    # The output is mostly fine - it references tool calls for resources
    # Just clean up any excessive whitespace
    output = re.sub(r'\n{3,}', '\n\n', output)
    return output.strip()


def transform_example(example: dict) -> dict:
    """Transform a single training example to the new format."""
    instruction = example.get('instruction', '')
    output = example.get('output', '')

    # Extract user message from original instruction
    user_message = extract_user_message(instruction)

    # Create new instruction
    new_instruction = NEW_INSTRUCTION_TEMPLATE.format(user_message=user_message)

    # Clean output
    cleaned_output = clean_output(output)

    return {
        'instruction': new_instruction,
        'input': '',  # Keep empty as in original
        'output': cleaned_output
    }


def transform_file(input_path: Path, output_path: Path) -> dict:
    """Transform entire training file and return statistics."""
    stats = {
        'total': 0,
        'transformed': 0,
        'errors': 0,
        'risk_levels': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    }

    transformed_examples = []

    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            stats['total'] += 1

            try:
                example = json.loads(line)
                transformed = transform_example(example)
                transformed_examples.append(transformed)
                stats['transformed'] += 1

                # Count risk levels
                output = transformed['output']
                for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                    if f'RISK LEVEL: {level}' in output or f'RISK LEVEL: {level} ' in output:
                        stats['risk_levels'][level] += 1
                        break

            except json.JSONDecodeError as e:
                print(f"Line {line_num}: JSON error - {e}")
                stats['errors'] += 1
            except Exception as e:
                print(f"Line {line_num}: Error - {e}")
                stats['errors'] += 1

    # Write transformed data
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in transformed_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    return stats


def main():
    input_file = Path('Fine Tuning/training-data.jsonl')
    output_file = Path('Fine Tuning/training-data-v2.jsonl')

    if not input_file.exists():
        print(f"Error: {input_file} not found")
        return

    print(f"Transforming {input_file} -> {output_file}")
    print("=" * 60)

    stats = transform_file(input_file, output_file)

    print(f"\nResults:")
    print(f"  Total examples: {stats['total']}")
    print(f"  Transformed: {stats['transformed']}")
    print(f"  Errors: {stats['errors']}")
    print(f"\nRisk level distribution:")
    for level, count in stats['risk_levels'].items():
        pct = (count / stats['transformed'] * 100) if stats['transformed'] > 0 else 0
        print(f"  {level}: {count} ({pct:.1f}%)")

    # Show sample of transformed data
    print("\n" + "=" * 60)
    print("Sample transformed example:")
    print("=" * 60)

    with open(output_file, 'r', encoding='utf-8') as f:
        sample = json.loads(f.readline())
        print(f"\nINSTRUCTION:\n{sample['instruction']}")
        print(f"\nOUTPUT:\n{sample['output']}")


if __name__ == '__main__':
    main()
