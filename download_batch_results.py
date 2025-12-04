#!/usr/bin/env python3
"""
Download and process batch results from Anthropic API.

Uses the guardian_llm.data_utils module for consistent V2 formatting.

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

# Use the guardian_llm module for consistent formatting
try:
    from guardian_llm.data_utils import (
        process_batch_results,
        normalize_dataset,
        INSTRUCTION_TEMPLATE_V2
    )
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

    # Process into training format using V2 template
    print("\nProcessing into training format (V2)...")

    output_file = "supplementary_training_data.jsonl"

    if USE_MODULE:
        created, errors = process_batch_results(
            Path(results_file),
            Path(output_file),
            INSTRUCTION_TEMPLATE_V2
        )
        print(f"\n✓ Created {created} training entries")
        if errors:
            print(f"⚠ Errors: {errors}")
    else:
        # Fallback processing
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
                                "instruction": INSTRUCTION_TEMPLATE_V2.format(user_message=user_msg),
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

    # Normalize the output to ensure consistent tool calling
    if USE_MODULE:
        print("\nNormalizing output (ensuring consistent tool calls)...")
        normalized_file = "supplementary_training_data_normalized.jsonl"
        stats = normalize_dataset(
            Path(output_file),
            Path(normalized_file),
            INSTRUCTION_TEMPLATE_V2,
            ensure_tool_calls=True
        )
        print(f"  Tools added: {stats['tools_added']}")
        print(f"  Tools removed: {stats['tools_removed']}")
        print(f"  Normalized file: {normalized_file}")
        output_file = normalized_file

    # Create combined dataset
    combined_file = "combined_training_data.jsonl"
    original_file = "Fine Tuning/training-data-final.jsonl"

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

        # Normalize the combined file
        if USE_MODULE:
            print("\nNormalizing combined dataset...")
            combined_normalized = "combined_training_data_final.jsonl"
            stats = normalize_dataset(
                Path(combined_file),
                Path(combined_normalized),
                INSTRUCTION_TEMPLATE_V2,
                ensure_tool_calls=True
            )
            print(f"  Final normalized file: {combined_normalized}")
    else:
        print(f"\nNote: {original_file} not found, skipping combine step")
        print(f"Use the supplementary file directly: {output_file}")


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
