#!/usr/bin/env python3
"""
Build Guardian Alpaca training dataset from modular components:
- instructions.jsonl: System instruction templates
- prompts.jsonl: User observations/prompts
- outputs.jsonl: Expected AI responses

Combines them into guardian-alpaca-built.jsonl
"""

import json
from pathlib import Path

def main():
    # File paths
    instructions_file = Path('instructions.jsonl')
    prompts_file = Path('prompts.jsonl')
    outputs_file = Path('outputs.jsonl')
    output_file = Path('guardian-alpaca-built.jsonl')

    # Check files exist
    missing_files = []
    for file in [instructions_file, prompts_file, outputs_file]:
        if not file.exists():
            missing_files.append(str(file))

    if missing_files:
        print("❌ Error: Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return

    print("Reading component files...")

    # Load instructions
    instructions = {}
    with open(instructions_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                inst = json.loads(line)
                instructions[inst['id']] = inst['template']
    print(f"  ✓ Loaded {len(instructions)} instruction template(s)")

    # Load outputs
    outputs = {}
    with open(outputs_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                output = json.loads(line)
                outputs[output['id']] = output['text']
    print(f"  ✓ Loaded {len(outputs)} output(s)")

    # Load prompts and build dataset
    prompts = []
    with open(prompts_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                prompts.append(json.loads(line))
    print(f"  ✓ Loaded {len(prompts)} prompt(s)")

    # Build full dataset
    print("\nBuilding full training dataset...")
    built_entries = []
    warnings = []

    for i, prompt in enumerate(prompts, 1):
        # Get instruction template
        instruction_template = instructions.get(prompt['instruction_template'])
        if not instruction_template:
            warnings.append(f"Prompt {prompt['id']}: Missing instruction template '{prompt['instruction_template']}'")
            continue

        # Get output
        output_text = outputs.get(prompt['output_id'])
        if not output_text:
            warnings.append(f"Prompt {prompt['id']}: Missing output '{prompt['output_id']}'")
            continue

        # Combine into full entry
        full_instruction = instruction_template + prompt['text']

        entry = {
            'instruction': full_instruction,
            'input': '',  # Empty as per original format
            'output': output_text
        }

        built_entries.append(entry)

    print(f"  ✓ Built {len(built_entries)} training entries")

    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):")
        for warning in warnings[:10]:  # Show first 10
            print(f"   - {warning}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more")

    # Write output file
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in built_entries:
            f.write(json.dumps(entry) + '\n')

    print(f"\n✅ Dataset built successfully!")
    print(f"   Output: {output_file}")
    print(f"   Entries: {len(built_entries)}")
    print("\nYou can now use this file for fine-tuning Guardian AI.")

if __name__ == '__main__':
    main()
