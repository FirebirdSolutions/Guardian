#!/usr/bin/env python3
"""
Fix training data format for Qwen tool calling.

This script:
1. Converts ALL [TOOL_CALL: function(...)] to <tool_call> JSON format
2. Keeps ONLY get_crisis_resources() - removes log_incident() for simplicity
3. Ensures clean output boundaries (no trailing incomplete content)
4. Normalizes whitespace and formatting
"""

import json
import re
from pathlib import Path


def parse_old_tool_call(tool_call_str: str) -> dict:
    """Parse old format [TOOL_CALL: func(args)] into structured data."""
    # Extract function name and arguments
    match = re.match(r'\[TOOL_CALL:\s*(\w+)\(([^)]*)\)\]', tool_call_str, re.DOTALL)
    if not match:
        # Try alternate format without closing bracket
        match = re.match(r'\[TOOL_CALL:\s*(\w+)\((.+)', tool_call_str, re.DOTALL)
        if not match:
            return None

    func_name = match.group(1)
    args_str = match.group(2).strip()

    # Skip log_incident - we're simplifying to just get_crisis_resources
    if func_name == 'log_incident':
        return None

    arguments = {}

    if func_name == 'get_crisis_resources':
        # Extract region and situation_type
        region_match = re.search(r"region=['\"]?(\w+)['\"]?", args_str)
        situation_match = re.search(r"situation_type=['\"]?([\w_]+)['\"]?", args_str)

        arguments['region'] = region_match.group(1) if region_match else 'NZ'
        arguments['situation_type'] = situation_match.group(1) if situation_match else 'mental_health'

    return {
        'name': func_name,
        'arguments': arguments
    }


def convert_to_qwen_format(tool_call_data: dict) -> str:
    """Convert tool call dict to Qwen's native format - single line for clarity."""
    args_json = json.dumps(tool_call_data['arguments'])
    return f'<tool_call>{{"name": "{tool_call_data["name"]}", "arguments": {args_json}}}</tool_call>'


def fix_output(output: str, risk_level: str) -> str:
    """Fix output to use proper Qwen tool call format with single get_crisis_resources."""

    # Remove debug artifacts that got accidentally included
    # Pattern: , 'user_message': '...'})] or similar (single or double quotes)
    output = re.sub(r",\s*'user_message':\s*['\"][^'\"]*['\"][^)]*\)\s*\]", '', output)
    output = re.sub(r",\s*'user_message':\s*['\"][^'\"]*\.\.\.['\"][^)]*\)\s*\]", '', output)
    # Handle double-quoted keys too
    output = re.sub(r',\s*"user_message":\s*["\'][^"\']*["\'][^)]*\)\s*\]', '', output)
    # Also handle just the })] ending
    output = re.sub(r"\}\s*\)\s*\]\s*$", '', output)

    # First, remove all log_incident calls (both old and new format)
    # Remove old format log_incident (case-insensitive)
    output = re.sub(r'\[TOOL_CALL:\s*log_incident\([^]]+\)\]', '', output, flags=re.IGNORECASE)
    # Also handle [TOOL_call: variant
    output = re.sub(r'\[TOOL_call:\s*log_incident\([^]]+\)\]', '', output, flags=re.IGNORECASE)
    # Remove new format log_incident
    output = re.sub(r'<tool_call>\s*\{[^}]*"name":\s*"log_incident"[^}]*\}[^<]*</tool_call>', '', output, flags=re.DOTALL)

    # Find all old-style get_crisis_resources calls
    old_pattern = r'\[TOOL_CALL:\s*get_crisis_resources\([^]]+\)\]'

    def replace_tool_call(match):
        old_call = match.group(0)
        parsed = parse_old_tool_call(old_call)
        if parsed:
            return convert_to_qwen_format(parsed)
        return ''  # Remove if can't parse

    # Replace all old-style get_crisis_resources calls
    fixed = re.sub(old_pattern, replace_tool_call, output)

    # Also handle remaining old format that didn't match
    remaining_old = re.findall(r'\[TOOL_CALL:[^]]+\]', fixed)
    for old_call in remaining_old:
        parsed = parse_old_tool_call(old_call)
        if parsed:
            fixed = fixed.replace(old_call, convert_to_qwen_format(parsed))
        else:
            fixed = fixed.replace(old_call, '')  # Remove log_incident or unparseable

    # Check if we have get_crisis_resources call - if risk is CRITICAL/HIGH/MEDIUM and no tool call, add one
    has_tool_call = '<tool_call>' in fixed
    if not has_tool_call and risk_level in ['CRITICAL', 'HIGH', 'MEDIUM']:
        # Determine situation type based on content
        output_lower = fixed.lower()
        if 'domestic' in output_lower or 'violence' in output_lower or 'hit' in output_lower or 'abuse' in output_lower:
            situation = 'domestic_violence'
        elif 'suicid' in output_lower or 'kill' in output_lower or 'die' in output_lower or 'end' in output_lower:
            situation = 'mental_health'
        elif 'self-harm' in output_lower or 'cutting' in output_lower or 'hurt myself' in output_lower:
            situation = 'self_harm'
        else:
            situation = 'mental_health'

        tool_call = f'<tool_call>{{"name": "get_crisis_resources", "arguments": {{"region": "NZ", "situation_type": "{situation}"}}}}</tool_call>'

        # Insert after ACTION line
        action_match = re.search(r'(ACTION:[^\n]*\n)', fixed)
        if action_match:
            insert_pos = action_match.end()
            fixed = fixed[:insert_pos] + '\n' + tool_call + '\n' + fixed[insert_pos:]
        else:
            # Insert after first line
            first_newline = fixed.find('\n')
            if first_newline > 0:
                fixed = fixed[:first_newline+1] + '\n' + tool_call + '\n' + fixed[first_newline+1:]

    # Remove LOW risk tool calls if any snuck in
    if risk_level == 'LOW' and '<tool_call>' in fixed:
        fixed = re.sub(r'<tool_call>[^<]*</tool_call>\n?', '', fixed)

    # Clean up multiple consecutive newlines
    fixed = re.sub(r'\n{3,}', '\n\n', fixed)

    # Strip trailing whitespace
    fixed = fixed.rstrip()

    return fixed


def extract_risk_level(output: str) -> str:
    """Extract risk level from output."""
    match = re.search(r'RISK LEVEL:\s*(CRITICAL|HIGH|MEDIUM|LOW)', output, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return 'MEDIUM'


def process_file(input_path: str, output_path: str):
    """Process the training file and fix all formatting issues."""

    input_file = Path(input_path)
    output_file = Path(output_path)

    fixed_count = 0
    log_removed_count = 0
    tool_added_count = 0
    total_count = 0

    stats = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    tool_stats = {'with_tool': 0, 'no_tool': 0}

    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:

        for line in f_in:
            total_count += 1
            data = json.loads(line)

            original_output = data.get('output', '')
            risk_level = extract_risk_level(original_output)
            stats[risk_level] = stats.get(risk_level, 0) + 1

            had_log_incident = 'log_incident' in original_output
            had_old_format = '[TOOL_CALL:' in original_output
            had_tool = '<tool_call>' in original_output or had_old_format

            # Fix the output
            data['output'] = fix_output(original_output, risk_level)

            if had_old_format:
                fixed_count += 1
            if had_log_incident:
                log_removed_count += 1
            if not had_tool and '<tool_call>' in data['output']:
                tool_added_count += 1

            # Track final tool stats
            if '<tool_call>' in data['output']:
                tool_stats['with_tool'] += 1
            else:
                tool_stats['no_tool'] += 1

            f_out.write(json.dumps(data, ensure_ascii=False) + '\n')

    print(f"Processed {total_count} examples")
    print(f"\nRisk level distribution:")
    for level, count in sorted(stats.items(), key=lambda x: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].index(x[0])):
        print(f"  {level}: {count}")
    print(f"\nChanges made:")
    print(f"  - Fixed old [TOOL_CALL:] format: {fixed_count}")
    print(f"  - Removed log_incident calls: {log_removed_count}")
    print(f"  - Added missing tool calls: {tool_added_count}")
    print(f"\nFinal tool call stats:")
    print(f"  - With get_crisis_resources: {tool_stats['with_tool']}")
    print(f"  - Without tool call (LOW risk): {tool_stats['no_tool']}")
    print(f"\nOutput saved to: {output_path}")


def validate_output(file_path: str):
    """Validate that all outputs are properly formatted."""
    issues = []
    risk_tool_issues = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line)
            output = data.get('output', '')
            risk = extract_risk_level(output)

            # Check for remaining old format
            if '[TOOL_CALL:' in output:
                issues.append(f"Line {i}: Still has [TOOL_CALL: format")

            # Check for log_incident (should be removed)
            if 'log_incident' in output:
                issues.append(f"Line {i}: Still has log_incident")

            # Check for unclosed tool calls
            open_tags = output.count('<tool_call>')
            close_tags = output.count('</tool_call>')
            if open_tags != close_tags:
                issues.append(f"Line {i}: Mismatched tool_call tags ({open_tags} open, {close_tags} close)")

            # Check risk level vs tool call consistency
            has_tool = '<tool_call>' in output
            if risk in ['CRITICAL', 'HIGH', 'MEDIUM'] and not has_tool:
                risk_tool_issues.append(f"Line {i}: {risk} risk without tool call")
            if risk == 'LOW' and has_tool:
                risk_tool_issues.append(f"Line {i}: LOW risk with tool call")

    if issues:
        print(f"\nFound {len(issues)} format issues:")
        for issue in issues[:10]:
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("\n✓ All outputs properly formatted!")

    if risk_tool_issues:
        print(f"\nFound {len(risk_tool_issues)} risk/tool mismatches:")
        for issue in risk_tool_issues[:5]:
            print(f"  - {issue}")
        if len(risk_tool_issues) > 5:
            print(f"  ... and {len(risk_tool_issues) - 5} more")
    else:
        print("✓ All risk levels match tool call presence!")

    return len(issues) == 0 and len(risk_tool_issues) == 0


if __name__ == '__main__':
    import sys

    # Default paths
    input_file = "guardian_llm/data/guardian-training-qwen-format.jsonl"
    output_file = "guardian_llm/data/guardian-training-qwen-fixed.jsonl"

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]

    print(f"Fixing training data format...")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"\nSimplification: Keeping ONLY get_crisis_resources()")
    print(f"               Removing all log_incident() calls")
    print()

    process_file(input_file, output_file)
    print()

    # Validate
    print("Validating output...")
    validate_output(output_file)
