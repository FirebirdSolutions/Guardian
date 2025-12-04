#!/usr/bin/env python3
"""
Guardian Training Data Preparation

Combines both transformations:
1. Clean instruction format (removes hardcoded resources from instruction)
2. Consistent tool calling (Option B: CRITICAL/HIGH/MEDIUM get tools, LOW doesn't)

This produces the final recommended training file.
"""

import json
import re
from pathlib import Path


# Clean instruction template
INSTRUCTION_TEMPLATE = """You are Guardian, an AI crisis detection system for New Zealand.

Your role:
- Analyze messages for crisis indicators (mental health, domestic violence, self-harm, etc.)
- Classify risk level: CRITICAL, HIGH, MEDIUM, or LOW
- For CRITICAL/HIGH/MEDIUM: Use tool calls to get verified crisis resources
- Never hallucinate resources - always use get_crisis_resources() tool
- Respond with empathy and accuracy

Analyze this message:
User: '{user_message}'"""


def extract_user_message(instruction: str) -> str:
    """Extract the user message from original instruction."""
    match = re.search(r"Observation:\s*User:\s*['\"](.+?)['\"]$", instruction, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"User:\s*['\"](.+?)['\"]$", instruction, re.DOTALL)
    if match:
        return match.group(1).strip()
    return instruction


def extract_risk_level(output: str) -> str:
    """Extract risk level from output."""
    match = re.search(r'RISK LEVEL:\s*(CRITICAL|HIGH|MEDIUM|LOW)', output, re.IGNORECASE)
    return match.group(1).upper() if match else 'UNKNOWN'


def get_situation_type(risk_level: str) -> str:
    """Map risk level to situation type for tool calls."""
    mapping = {
        'CRITICAL': 'emergency',
        'HIGH': 'crisis',
        'MEDIUM': 'support'
    }
    return mapping.get(risk_level, 'support')


def has_tool_call(output: str) -> bool:
    """Check if output contains a tool call."""
    return '[TOOL_CALL:' in output


def add_tool_call(output: str, risk_level: str) -> str:
    """Add appropriate tool call if missing."""
    situation_type = get_situation_type(risk_level)
    tool_call = f"\n\n[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='{situation_type}')]"

    # Insert after ACTION line if present
    if 'ACTION:' in output:
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('ACTION:'):
                lines.insert(i + 1, tool_call.strip())
                return '\n'.join(lines)

    # Otherwise insert after PATTERNS DETECTED
    if 'PATTERNS DETECTED:' in output:
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('PATTERNS DETECTED:'):
                lines.insert(i + 1, tool_call.strip())
                return '\n'.join(lines)

    # Fallback: insert after first line
    lines = output.split('\n')
    lines.insert(1, tool_call.strip())
    return '\n'.join(lines)


def remove_tool_calls(output: str) -> str:
    """Remove all tool calls from output."""
    output = re.sub(r'\n*\[TOOL_CALL:[^\]]+\]', '', output)
    return re.sub(r'\n{3,}', '\n\n', output).strip()


def process_example(example: dict) -> dict:
    """Process a single training example with both transformations."""
    instruction = example.get('instruction', '')
    output = example.get('output', '')

    # 1. Extract user message and create clean instruction
    user_message = extract_user_message(instruction)
    clean_instruction = INSTRUCTION_TEMPLATE.format(user_message=user_message)

    # 2. Extract risk level
    risk_level = extract_risk_level(output)

    # 3. Normalize tool calls based on risk level
    has_tool = has_tool_call(output)

    if risk_level in ['CRITICAL', 'HIGH', 'MEDIUM']:
        # Should have tool calls
        if not has_tool:
            output = add_tool_call(output, risk_level)
    elif risk_level == 'LOW':
        # Should NOT have tool calls
        if has_tool:
            output = remove_tool_calls(output)

    # 4. Clean up output
    output = re.sub(r'\n{3,}', '\n\n', output).strip()

    return {
        'instruction': clean_instruction,
        'input': '',
        'output': output,
        'metadata': {
            'risk_level': risk_level,
            'has_tool_call': has_tool_call(output),
            'situation_type': get_situation_type(risk_level) if risk_level != 'LOW' else None
        }
    }


def main():
    input_path = Path('Fine Tuning/training-data.jsonl')
    output_path = Path('Fine Tuning/training-data-final.jsonl')

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        return

    print("Guardian Training Data Preparation")
    print("=" * 60)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print()

    stats = {
        'total': 0,
        'processed': 0,
        'risk_levels': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0},
        'tools_added': 0,
        'tools_removed': 0
    }

    processed = []

    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            stats['total'] += 1

            try:
                original = json.loads(line)
                original_has_tool = has_tool_call(original.get('output', ''))

                result = process_example(original)
                processed.append(result)
                stats['processed'] += 1

                # Track changes
                risk = result['metadata']['risk_level']
                stats['risk_levels'][risk] += 1

                new_has_tool = result['metadata']['has_tool_call']
                if not original_has_tool and new_has_tool:
                    stats['tools_added'] += 1
                elif original_has_tool and not new_has_tool:
                    stats['tools_removed'] += 1

            except Exception as e:
                print(f"Error processing line: {e}")

    # Write output (without metadata for training)
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in processed:
            training_item = {
                'instruction': item['instruction'],
                'input': item['input'],
                'output': item['output']
            }
            f.write(json.dumps(training_item, ensure_ascii=False) + '\n')

    # Print summary
    print("\nResults:")
    print(f"  Total examples: {stats['total']}")
    print(f"  Processed: {stats['processed']}")
    print(f"  Tool calls added: {stats['tools_added']}")
    print(f"  Tool calls removed: {stats['tools_removed']}")
    print()
    print("Risk Level Distribution:")
    for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = stats['risk_levels'][level]
        pct = (count / stats['processed'] * 100) if stats['processed'] > 0 else 0
        has_tools = "with tools" if level != 'LOW' else "no tools"
        print(f"  {level}: {count} ({pct:.1f}%) - {has_tools}")

    print()
    print(f"Final training file: {output_path}")
    print("=" * 60)

    # Show sample
    print("\nSample (first example):")
    print("-" * 40)
    sample = processed[0]
    print(f"INSTRUCTION:\n{sample['instruction'][:200]}...")
    print(f"\nOUTPUT:\n{sample['output'][:300]}...")


if __name__ == '__main__':
    main()
