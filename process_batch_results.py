#!/usr/bin/env python3
"""Process batch results and create final training dataset."""

import json
from pathlib import Path

def process_batch_results(results_file: str, output_file: str):
    """Convert batch results to alpaca training format."""

    instruction_template = """You are Guardian, an AI safety system.

VERIFIED NZ CRISIS RESOURCES:
• 111 - Emergency services
• 1737 - Mental health crisis (Free 24/7 call or text)
• 0800 543 354 - Lifeline NZ (Free 24/7)
• 0800 456 450 - Family Violence Hotline (Free 24/7)
• 0800 733 843 - Women's Refuge (Free 24/7)

KNOWN FAKE NUMBERS:
• 0800 543 800 - FAKE
• 988 - US crisis line (not NZ)

Observation: User: '{user_message}'"""

    training_entries = []
    errors = []

    with open(results_file, 'r') as f:
        for line in f:
            result = json.loads(line)
            custom_id = result.get("custom_id", "unknown")

            try:
                # Extract the response content
                content = result["result"]["message"]["content"][0]["text"]

                # Parse the JSON response
                variations = json.loads(content)

                for i, var in enumerate(variations.get("variations", [])):
                    user_msg = var.get("user_message", "")
                    output = var.get("output", "")

                    if user_msg and output:
                        training_entries.append({
                            "instruction": instruction_template.format(user_message=user_msg),
                            "input": "",
                            "output": output
                        })
                    else:
                        errors.append(f"{custom_id}_var{i}: Empty user_message or output")

            except (KeyError, json.JSONDecodeError) as e:
                errors.append(f"{custom_id}: {str(e)}")

    # Write training file
    with open(output_file, 'w') as f:
        for entry in training_entries:
            f.write(json.dumps(entry) + '\n')

    print(f"Created {len(training_entries)} training entries")
    print(f"Errors: {len(errors)}")
    if errors[:5]:
        print("First 5 errors:", errors[:5])

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python process_batch_results.py <results_file.jsonl> [output_file.jsonl]")
        sys.exit(1)

    results_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "supplementary_training_data.jsonl"
    process_batch_results(results_file, output_file)
