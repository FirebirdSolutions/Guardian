#!/usr/bin/env python3
"""
Download and process batch results from Anthropic API.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python3 download_batch_results.py <batch_id>

Or use the batch_id.txt file:
    python3 download_batch_results.py
"""

import anthropic
import argparse
import json
import os
import sys
from pathlib import Path

def download_and_process(api_key: str, batch_id: str):
    """Download batch results and convert to training format."""

    client = anthropic.Anthropic(api_key=api_key)

    # Check batch status
    print(f"Checking batch status for: {batch_id}")
    batch = client.batches.retrieve(batch_id)

    print(f"Status: {batch.processing_status}")
    print(f"Request counts: {batch.request_counts}")

    if batch.processing_status != "ended":
        print(f"\nBatch not complete yet. Current status: {batch.processing_status}")
        print("Please wait for the batch to complete and try again.")
        return

    # Download results
    print("\nDownloading results...")
    results_file = f"batch_results_{batch_id}.jsonl"

    results = list(client.batches.results(batch_id))

    with open(results_file, 'w') as f:
        for result in results:
            f.write(json.dumps(result.model_dump()) + '\n')

    print(f"Results saved to: {results_file}")

    # Process into training format
    print("\nProcessing into training format...")

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

    for result in results:
        custom_id = result.custom_id

        try:
            if result.result.type == "succeeded":
                content = result.result.message.content[0].text
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
                        errors.append(f"{custom_id}_var{i}: Empty content")
            else:
                errors.append(f"{custom_id}: {result.result.type}")

        except Exception as e:
            errors.append(f"{custom_id}: {str(e)}")

    # Write training file
    output_file = "supplementary_training_data.jsonl"
    with open(output_file, 'w') as f:
        for entry in training_entries:
            f.write(json.dumps(entry) + '\n')

    print(f"\n✓ Created {len(training_entries)} training entries")
    print(f"  Output file: {output_file}")

    if errors:
        print(f"\n⚠ Errors: {len(errors)}")
        error_file = "batch_errors.txt"
        with open(error_file, 'w') as f:
            for e in errors:
                f.write(e + '\n')
        print(f"  Error log: {error_file}")

    # Create combined dataset
    combined_file = "combined_training_data.jsonl"
    original_file = "Original-guardian-alpaca.jsonl"

    if Path(original_file).exists():
        print(f"\nCreating combined dataset...")
        with open(combined_file, 'w') as out:
            with open(original_file, 'r') as orig:
                for line in orig:
                    out.write(line)
            with open(output_file, 'r') as supp:
                for line in supp:
                    out.write(line)

        # Count final
        with open(combined_file, 'r') as f:
            total = sum(1 for _ in f)
        print(f"  Combined file: {combined_file}")
        print(f"  Total entries: {total}")

def main():
    parser = argparse.ArgumentParser(description="Download Guardian batch results")
    parser.add_argument("batch_id", nargs="?", help="Batch ID to download")
    parser.add_argument("--api-key", help="Anthropic API key")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: No API key. Set ANTHROPIC_API_KEY or use --api-key")
        sys.exit(1)

    batch_id = args.batch_id
    if not batch_id:
        batch_id_file = Path("batch_id.txt")
        if batch_id_file.exists():
            batch_id = batch_id_file.read_text().strip()
            print(f"Using batch ID from batch_id.txt: {batch_id}")
        else:
            print("Error: No batch ID provided and batch_id.txt not found")
            sys.exit(1)

    download_and_process(api_key, batch_id)

if __name__ == "__main__":
    main()
