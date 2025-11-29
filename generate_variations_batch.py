#!/usr/bin/env python3
"""
Generate Claude Batch API requests to create 3 language variations
per original Guardian training example.

This script creates a JSONL file suitable for the Anthropic Batch API.
"""

import json
import hashlib
from pathlib import Path

# Configuration
INPUT_FILE = "Original-guardian-alpaca.jsonl"
OUTPUT_BATCH_FILE = "batch_requests.jsonl"
MODEL = "claude-sonnet-4-20250514"  # or claude-3-haiku-20240307 for cost savings

# System prompt for the variation generator
SYSTEM_PROMPT = """You are helping create training data for Guardian, an AI crisis detection system for New Zealand.

Your task: Given an original user message and its corresponding Guardian response, generate 3 NEW variations of the user message that:
1. Express the SAME underlying situation/emotion/risk level
2. Use DIFFERENT wording, phrasing, sentence structure
3. Maintain the same cultural context (NZ)
4. Vary between formal/informal, verbose/terse, direct/indirect

For each variation, also generate the appropriate Guardian response following the EXACT same format as the original.

CRITICAL RULES:
- Keep the same risk level (CRITICAL/HIGH/MEDIUM/LOW)
- Use consistent tool call format: [TOOL_CALL: tool_name(params)]
- Only use VERIFIED NZ resources from the list provided
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
    if "Observation: User:" in instruction:
        return instruction.split("Observation: User:")[-1].strip().strip("'\"")
    return instruction

def create_instruction_template(user_message: str) -> str:
    """Create the standard instruction with a new user message."""
    return f"""You are Guardian, an AI safety system.

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
- Use [TOOL_CALL: ...] format (with underscore) for tool calls
- Only use verified NZ crisis resources
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
    input_path = Path(__file__).parent / INPUT_FILE
    output_path = Path(__file__).parent / OUTPUT_BATCH_FILE

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
    print(f"\nTo submit this batch, use:")
    print(f"  anthropic batch create --input-file {OUTPUT_BATCH_FILE}")

    # Also create a helper script to process results
    process_script = '''#!/usr/bin/env python3
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
            f.write(json.dumps(entry) + '\\n')

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
'''

    process_path = Path(__file__).parent / "process_batch_results.py"
    with open(process_path, 'w') as f:
        f.write(process_script)

    print(f"\nAlso created: {process_path}")
    print("Run this after batch completes to create training data")

if __name__ == "__main__":
    main()
