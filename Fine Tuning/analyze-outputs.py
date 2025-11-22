#!/usr/bin/env python3
"""
Analyze Guardian outputs to extract all tool calls and action patterns
"""

import json
import re
from collections import defaultdict
from pathlib import Path

def extract_tool_calls(output_text):
    """Extract all TOOL CALL patterns from output."""
    pattern = r'\[TOOL CALL:\s*([^\]]+)\]'
    matches = re.findall(pattern, output_text)

    tool_calls = []
    for match in matches:
        # Extract just the function name
        func_match = re.match(r'(\w+)\(', match)
        if func_match:
            tool_calls.append(func_match.group(1))

    return tool_calls

def extract_sections(output_text):
    """Extract major sections from output."""
    sections = defaultdict(bool)

    # Common sections
    if re.search(r'RISK LEVEL:', output_text, re.IGNORECASE):
        sections['risk_level'] = True
    if re.search(r'PATTERNS DETECTED:', output_text, re.IGNORECASE):
        sections['patterns_detected'] = True
    if re.search(r'ACTION:', output_text, re.IGNORECASE):
        sections['action'] = True
    if re.search(r'INTERVENTION:', output_text, re.IGNORECASE):
        sections['intervention'] = True
    if re.search(r'ESCALATE:', output_text, re.IGNORECASE):
        sections['escalate'] = True
    if re.search(r'TONE:', output_text, re.IGNORECASE):
        sections['tone'] = True
    if re.search(r'NOTE:', output_text, re.IGNORECASE):
        sections['note'] = True
    if re.search(r'ALERT:', output_text, re.IGNORECASE):
        sections['alert'] = True
    if re.search(r'GUIDANCE:', output_text, re.IGNORECASE):
        sections['guidance'] = True
    if re.search(r'REASSURANCE:', output_text, re.IGNORECASE):
        sections['reassurance'] = True
    if re.search(r'SAFETY CHECK:', output_text, re.IGNORECASE):
        sections['safety_check'] = True
    if re.search(r'RESOURCE VERIFICATION', output_text, re.IGNORECASE):
        sections['resource_verification'] = True
    if re.search(r'HALLUCINATION DETECTED:', output_text, re.IGNORECASE):
        sections['hallucination_detected'] = True
    if re.search(r'TOOL STATUS:', output_text, re.IGNORECASE):
        sections['tool_status'] = True
    if re.search(r'ASSESSMENT:', output_text, re.IGNORECASE):
        sections['assessment'] = True
    if re.search(r'MEDICAL', output_text, re.IGNORECASE):
        sections['medical_concern'] = True
    if re.search(r'CONTEXT', output_text, re.IGNORECASE):
        sections['context'] = True
    if re.search(r'SPECIAL CONSIDERATIONS:', output_text, re.IGNORECASE):
        sections['special_considerations'] = True
    if re.search(r'MANDATORY REPORTING', output_text, re.IGNORECASE):
        sections['mandatory_reporting'] = True
    if re.search(r'SOURCE:', output_text, re.IGNORECASE):
        sections['source'] = True
    if re.search(r'CRIMINAL BEHAVIOR:', output_text, re.IGNORECASE):
        sections['criminal_behavior'] = True
    if re.search(r'SERVICE FAILURE', output_text, re.IGNORECASE):
        sections['service_failure'] = True

    return sections

def main():
    outputs_file = Path('outputs.jsonl')

    if not outputs_file.exists():
        print("Error: outputs.jsonl not found!")
        return

    all_tool_calls = defaultdict(int)
    all_sections = defaultdict(int)

    print("Analyzing outputs.jsonl...\n")

    with open(outputs_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            output = json.loads(line)

            # Extract tool calls
            tool_calls = extract_tool_calls(output['text'])
            for tool in tool_calls:
                all_tool_calls[tool] += 1

            # Extract sections
            sections = extract_sections(output['text'])
            for section in sections:
                all_sections[section] += 1

    print("=" * 60)
    print("TOOL CALLS FOUND")
    print("=" * 60)
    for tool, count in sorted(all_tool_calls.items(), key=lambda x: -x[1]):
        print(f"  {tool:40} {count:3} times")

    print("\n" + "=" * 60)
    print("SECTIONS/COMPONENTS FOUND")
    print("=" * 60)
    for section, count in sorted(all_sections.items(), key=lambda x: -x[1]):
        print(f"  {section:40} {count:3} times")

    print("\n" + "=" * 60)
    print("TOTAL STATISTICS")
    print("=" * 60)
    print(f"  Unique tool calls: {len(all_tool_calls)}")
    print(f"  Unique sections: {len(all_sections)}")

if __name__ == '__main__':
    main()
