#!/usr/bin/env python3
"""
Process batch results and create final training dataset.

This script is a simpler alternative to download_batch_results.py
for when you already have the results file downloaded.

Uses the V2 format with clean instructions and consistent tool calling.
"""

import json
import sys
from pathlib import Path

# Use the guardian_llm module for consistent formatting
try:
    from guardian_llm.data_utils import process_batch_results, INSTRUCTION_TEMPLATE_V2
    USE_MODULE = True
except ImportError:
    USE_MODULE = False
    INSTRUCTION_TEMPLATE_V2 = """You are Guardian, an AI crisis detection system for New Zealand.

Your role:
- Analyze messages for crisis indicators (mental health, domestic violence, self-harm, etc.)
- Classify risk level: CRITICAL, HIGH, MEDIUM, or LOW
- For CRITICAL/HIGH/MEDIUM: Use tool calls to get verified crisis resources
- Never hallucinate resources - always use get_crisis_resources() tool
- Respond with empathy and accuracy

Analyze this message:
User: '{user_message}'"""


def process_results(results_file: str, output_file: str):
    """Convert batch results to training format."""

    if USE_MODULE:
        created, errors = process_batch_results(
            Path(results_file),
            Path(output_file),
            INSTRUCTION_TEMPLATE_V2
        )
        print(f"Created {created} training entries")
        print(f"Errors: {errors}")
    else:
        # Fallback processing
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
                                "instruction": INSTRUCTION_TEMPLATE_V2.format(user_message=user_msg),
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
    if len(sys.argv) < 2:
        print("""
Usage: python process_batch_results.py <results_file.jsonl> [output_file.jsonl]

Processes Anthropic batch API results into Guardian training data.
Uses the V2 format with clean instructions.

Example:
  python process_batch_results.py batch_results.jsonl supplementary_training.jsonl
        """)
        sys.exit(1)

    results_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "supplementary_training_data.jsonl"
    process_results(results_file, output_file)
