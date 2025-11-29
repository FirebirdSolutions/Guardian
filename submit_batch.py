#!/usr/bin/env python3
"""
Submit batch job to Anthropic API for Guardian training data generation.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python3 submit_batch.py

Or:
    python3 submit_batch.py --api-key "your-key-here"
"""

import anthropic
import argparse
import os
import sys
from pathlib import Path

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

    print(f"\n✓ Batch submitted successfully!")
    print(f"  Batch ID: {batch.id}")
    print(f"  Status: {batch.processing_status}")
    print(f"  Created: {batch.created_at}")

    print(f"\nTo check status:")
    print(f"  python3 -c \"import anthropic; c = anthropic.Anthropic(); print(c.batches.retrieve('{batch.id}').processing_status)\"")

    print(f"\nTo download results when complete:")
    print(f"  python3 download_batch_results.py {batch.id}")

    # Save batch ID for later reference
    with open("batch_id.txt", "w") as f:
        f.write(batch.id)
    print(f"\nBatch ID saved to: batch_id.txt")

    return batch.id

def main():
    parser = argparse.ArgumentParser(description="Submit Guardian training data batch job")
    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    parser.add_argument("--input-file", default="batch_requests.jsonl", help="Input JSONL file")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: No API key provided")
        print("Set ANTHROPIC_API_KEY environment variable or use --api-key flag")
        sys.exit(1)

    submit_batch(api_key, args.input_file)

if __name__ == "__main__":
    main()
