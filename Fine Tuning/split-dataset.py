#!/usr/bin/env python3
"""
Split Guardian Alpaca JSONL into modular components:
- instructions.jsonl: System instruction templates
- prompts.jsonl: User observations/prompts
- outputs.jsonl: Expected AI responses categorized by type
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def extract_observation(instruction_text):
    """Extract the observation part from the instruction."""
    match = re.search(r'Observation:\s*(.*?)$', instruction_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def extract_base_instruction(instruction_text):
    """Extract the base instruction template (without observation)."""
    # Split at "Observation:" and take everything before
    parts = instruction_text.split('Observation:')
    if len(parts) > 0:
        return parts[0].strip() + '\n\nObservation: '
    return instruction_text

def categorize_output(output_text):
    """Categorize output by risk level and situation type."""
    category = {
        'risk_level': 'UNKNOWN',
        'situation_type': 'general',
        'patterns': []
    }

    # Extract risk level
    risk_match = re.search(r'RISK LEVEL:\s*(\w+(?:\s*-\s*\w+)*)', output_text, re.IGNORECASE)
    if risk_match:
        category['risk_level'] = risk_match.group(1).strip()

    # Extract patterns
    patterns_match = re.search(r'PATTERNS DETECTED:\s*([^\n]+)', output_text, re.IGNORECASE)
    if patterns_match:
        category['patterns'] = [p.strip() for p in patterns_match.group(1).split(',')]

    # Determine situation type from patterns and content
    output_lower = output_text.lower()
    if 'suicide' in output_lower or 'kill myself' in output_lower:
        category['situation_type'] = 'suicide'
    elif 'self-harm' in output_lower or 'self harm' in output_lower or 'cutting' in output_lower:
        category['situation_type'] = 'self_harm'
    elif 'domestic violence' in output_lower or 'family violence' in output_lower:
        category['situation_type'] = 'domestic_violence'
    elif 'child abuse' in output_lower or 'child protection' in output_lower:
        category['situation_type'] = 'child_abuse'
    elif 'eating disorder' in output_lower:
        category['situation_type'] = 'eating_disorder'
    elif 'substance' in output_lower or 'relapse' in output_lower or 'addiction' in output_lower:
        category['situation_type'] = 'substance_abuse'
    elif 'hallucination' in output_lower or 'fake' in output_lower:
        category['situation_type'] = 'hallucination_detection'
    elif 'stalking' in output_lower or 'harassment' in output_lower:
        category['situation_type'] = 'stalking_harassment'
    elif 'psychotic' in output_lower or 'psychosis' in output_lower:
        category['situation_type'] = 'psychosis'
    elif 'hopeless' in output_lower or 'mental health' in output_lower:
        category['situation_type'] = 'mental_health'
    elif 'service' in output_lower and 'fail' in output_lower:
        category['situation_type'] = 'service_failure'
    elif 'work stress' in output_lower:
        category['situation_type'] = 'work_stress'

    return category

def main():
    input_file = Path('guardian-alpaca.jsonl')

    if not input_file.exists():
        print(f"Error: {input_file} not found!")
        return

    # Storage
    instruction_templates = {}
    prompts = []
    outputs = defaultdict(list)

    print("Reading and analyzing guardian-alpaca.jsonl...")

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)

                # Extract base instruction template
                base_instruction = extract_base_instruction(entry['instruction'])
                if base_instruction not in instruction_templates:
                    template_id = f"template_{len(instruction_templates) + 1}"
                    instruction_templates[base_instruction] = template_id

                # Extract observation (prompt)
                observation = extract_observation(entry['instruction'])

                # Categorize output
                output_category = categorize_output(entry['output'])

                # Store prompt with metadata
                prompts.append({
                    'id': f'prompt_{line_num}',
                    'text': observation,
                    'instruction_template': instruction_templates[base_instruction],
                    'output_id': None  # Will be set later
                })

                # Store output with category
                output_id = f'output_{line_num}'
                outputs[output_category['situation_type']].append({
                    'id': output_id,
                    'text': entry['output'],
                    'risk_level': output_category['risk_level'],
                    'situation_type': output_category['situation_type'],
                    'patterns': output_category['patterns']
                })

                # Link prompt to output
                prompts[-1]['output_id'] = output_id

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue

    print(f"\nAnalysis complete!")
    print(f"  - {len(instruction_templates)} unique instruction template(s)")
    print(f"  - {len(prompts)} prompts")
    print(f"  - {sum(len(v) for v in outputs.values())} outputs across {len(outputs)} categories")

    # Write instruction templates
    print("\nWriting instructions.jsonl...")
    with open('instructions.jsonl', 'w', encoding='utf-8') as f:
        for template, template_id in instruction_templates.items():
            f.write(json.dumps({
                'id': template_id,
                'template': template
            }) + '\n')

    # Write prompts
    print("Writing prompts.jsonl...")
    with open('prompts.jsonl', 'w', encoding='utf-8') as f:
        for prompt in prompts:
            f.write(json.dumps(prompt) + '\n')

    # Write outputs
    print("Writing outputs.jsonl...")
    with open('outputs.jsonl', 'w', encoding='utf-8') as f:
        for category, output_list in sorted(outputs.items()):
            for output in output_list:
                f.write(json.dumps(output) + '\n')

    # Print category statistics
    print("\nOutput categories:")
    for category, output_list in sorted(outputs.items()):
        print(f"  - {category}: {len(output_list)} outputs")

    print("\n✅ Split complete! Files created:")
    print("   - instructions.jsonl")
    print("   - prompts.jsonl")
    print("   - outputs.jsonl")

if __name__ == '__main__':
    main()
