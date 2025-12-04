#!/usr/bin/env python3
"""
Submit batch job to Anthropic API for Guardian training data generation.

Uses the guardian_llm.data_utils module for consistent formatting.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python -m guardian_llm.scripts.batch_submit

Or:
    python -m guardian_llm.scripts.batch_submit --api-key "your-key-here" --input seeds.jsonl
"""

import anthropic
import argparse
import json
import os
import re
import sys
from pathlib import Path

from guardian_llm.data_utils import prepare_batch_requests, BATCH_GENERATION_PROMPT


def create_seed_examples_from_existing(training_file: str, sample_size: int = 100) -> list:
    """Extract seed examples from existing training data for variation generation."""
    seeds = []

    with open(training_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= sample_size:
                break

            try:
                data = json.loads(line)
                # Extract user message from instruction
                instruction = data.get('instruction', '')
                match = re.search(r"User:\s*['\"](.+?)['\"]", instruction, re.DOTALL)
                if match:
                    user_message = match.group(1).strip()

                    # Extract risk level from output
                    output = data.get('output', '')
                    risk_match = re.search(r'RISK LEVEL:\s*(\w+)', output, re.IGNORECASE)
                    risk_level = risk_match.group(1).upper() if risk_match else 'HIGH'

                    seeds.append({
                        'user_message': user_message,
                        'risk_level': risk_level
                    })
            except:
                continue

    return seeds


def submit_batch(api_key: str, input_file: str = "batch_requests.jsonl"):
    """Submit a batch job to Anthropic API."""

    client = anthropic.Anthropic(api_key=api_key)

    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    print(f"Reading batch requests from: {input_file}")

    # Count requests
    with open(input_path, 'r') as f:
        num_requests = sum(1 for _ in f)

    print(f"Found {num_requests} requests")
    print(f"Expected output: {num_requests * 3} training variations")
    print("\nSubmitting batch job...")

    # Submit the batch
    with open(input_path, 'rb') as f:
        batch = client.batches.create(
            requests=list(client.batches._parse_requests(f))
        )

    print(f"\n Batch submitted successfully!")
    print(f"  Batch ID: {batch.id}")
    print(f"  Status: {batch.processing_status}")
    print(f"  Created: {batch.created_at}")

    print(f"\nTo check status:")
    print(f"  python3 -c \"import anthropic; c = anthropic.Anthropic(); print(c.batches.retrieve('{batch.id}').processing_status)\"")

    print(f"\nTo download results when complete:")
    print(f"  python -m guardian_llm.scripts.batch_download {batch.id}")

    # Save batch ID for later reference
    with open("batch_id.txt", "w") as f:
        f.write(batch.id)
    print(f"\nBatch ID saved to: batch_id.txt")

    return batch.id


def main():
    parser = argparse.ArgumentParser(
        description="Submit Guardian training data batch job",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate batch requests from existing training data
  python -m guardian_llm.scripts.batch_submit --generate-from "Fine Tuning/training-data-final.jsonl" --sample 50

  # Submit existing batch requests file
  python -m guardian_llm.scripts.batch_submit --input-file batch_requests.jsonl
        """
    )
    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    parser.add_argument("--input-file", default="batch_requests.jsonl", help="Input JSONL file with batch requests")
    parser.add_argument("--generate-from", help="Generate batch requests from existing training file")
    parser.add_argument("--sample", type=int, default=100, help="Number of seeds to sample when generating")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: No API key provided")
        print("Set ANTHROPIC_API_KEY environment variable or use --api-key flag")
        sys.exit(1)

    # Generate batch requests if requested
    if args.generate_from:
        print(f"Generating batch requests from: {args.generate_from}")
        seeds = create_seed_examples_from_existing(args.generate_from, args.sample)

        count = prepare_batch_requests(seeds, Path(args.input_file))
        print(f"Created {count} batch requests -> {args.input_file}")

    submit_batch(api_key, args.input_file)


if __name__ == "__main__":
    main()
