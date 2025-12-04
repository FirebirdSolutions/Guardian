#!/usr/bin/env python3
"""
Generate Claude Batch API requests to create 3 language variations
per original Guardian training example.

This script creates a JSONL file suitable for the Anthropic Batch API.

Usage:
    python -m guardian_llm.scripts.generate_variations [input_file] [output_file]
"""

import json
import sys
from pathlib import Path

# Configuration
DEFAULT_INPUT_FILE = "guardian_llm/data/training-merged.jsonl"
DEFAULT_OUTPUT_FILE = "guardian_llm/data/batch_requests.jsonl"
# Use Claude 3.5 Sonnet for batch generation (update as newer models become available)
MODEL = "claude-3-5-sonnet-20241022"

# System prompt for the variation generator
SYSTEM_PROMPT = """You are helping create training data for Guardian, an AI crisis detection system.

Your task: Given an original user message and its corresponding Guardian response, generate 3 NEW variations of the user message that:
1. Express the SAME underlying situation/emotion/risk level
2. Use DIFFERENT wording, phrasing, sentence structure
3. Vary between formal/informal, verbose/terse, direct/indirect

For each variation, also generate the appropriate Guardian response following the EXACT same format as the original.

CRITICAL RULES:
- Keep the same risk level (CRITICAL/HIGH/MEDIUM/LOW)
- Use consistent tool call format: [TOOL_CALL: tool_name(params)]
- Use get_crisis_resources() tool for CRITICAL/HIGH/MEDIUM risk levels
- LOW risk level should NOT have tool calls
- Match the response structure and style of the original

Output as valid JSON with this structure:
{
  "variations": [
    {
      "user_message": "variation 1 text",
      "output": "full Guardian response for variation 1"
    },
    {
      "user_message": "variation 2 text",
      "output": "full Guardian response for variation 2"
    },
    {
      "user_message": "variation 3 text",
      "output": "full Guardian response for variation 3"
    }
  ]
}"""


def extract_user_message(instruction: str) -> str:
    """Extract the user message from the instruction field."""
    import re
    match = re.search(r"User:\s*['\"](.+?)['\"]", instruction, re.DOTALL)
    if match:
        return match.group(1).strip()
    return instruction


def generate_batch_request(entry: dict, entry_id: int) -> dict:
    """Generate a single batch API request for one original entry."""

    user_message = extract_user_message(entry.get("instruction", ""))
    original_output = entry.get("output", "")

    # Determine risk level from output
    risk_level = "UNKNOWN"
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if level in original_output:
            risk_level = level
            break

    user_prompt = f"""ORIGINAL USER MESSAGE:
"{user_message}"

RISK LEVEL: {risk_level}

ORIGINAL GUARDIAN RESPONSE:
{original_output}

---

Generate 3 variations of the user message (different wording, same meaning and risk level) with appropriate Guardian responses.

Remember:
- Use [TOOL_CALL: ...] format for tool calls
- CRITICAL/HIGH/MEDIUM should use get_crisis_resources() tool
- LOW should NOT have tool calls
- Match the response style and structure"""

    return {
        "custom_id": f"guardian_{entry_id:04d}",
        "params": {
            "model": MODEL,
            "max_tokens": 2048,
            "temperature": 0.7,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
    }


def main():
    input_file = DEFAULT_INPUT_FILE
    output_file = DEFAULT_OUTPUT_FILE

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]

    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Reading original dataset from: {input_path}")

    entries = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    print(f"Found {len(entries)} original entries")
    print(f"Will generate {len(entries) * 3} variations")

    # Generate batch requests
    batch_requests = []
    for i, entry in enumerate(entries):
        request = generate_batch_request(entry, i)
        batch_requests.append(request)

    # Write batch file
    with open(output_path, 'w', encoding='utf-8') as f:
        for request in batch_requests:
            f.write(json.dumps(request) + '\n')

    print(f"\nBatch request file written to: {output_path}")
    print(f"Total requests: {len(batch_requests)}")
    print(f"\nTo submit this batch:")
    print(f"  python -m guardian_llm.scripts.batch_submit --input-file {output_file}")


if __name__ == "__main__":
    main()
