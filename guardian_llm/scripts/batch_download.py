#!/usr/bin/env python3
"""
Download and process batch results from Anthropic API.

Uses the guardian_llm.data_utils module for consistent V2 formatting.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python -m guardian_llm.scripts.batch_download <batch_id>

Or use the batch_id.txt file:
    python -m guardian_llm.scripts.batch_download
"""

import anthropic
import argparse
import json
import os
import sys
from pathlib import Path

from guardian_llm.data_utils import (
    process_batch_results,
    normalize_dataset,
    INSTRUCTION_TEMPLATE_V2
)


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

    created, errors = process_batch_results(
        Path(results_file),
        Path(output_file),
        INSTRUCTION_TEMPLATE_V2
    )
    print(f"\n Created {created} training entries")
    if errors:
        print(f"  Errors: {errors}")

    # Normalize the output to ensure consistent tool calling
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
    combined_file = "guardian_llm/data/combined_training_data.jsonl"
    original_file = "guardian_llm/data/training-data-final.jsonl"

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
