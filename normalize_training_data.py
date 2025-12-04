#!/usr/bin/env python3
"""
Guardian Training Data Normalizer

Normalizes training data for consistent tool calling and adds metadata
for risk-level weighting during training.

Policy (Option B - Consistent Tool Usage):
- CRITICAL: get_crisis_resources(situation_type='emergency') + log_incident(severity='CRITICAL')
- HIGH: get_crisis_resources(situation_type='crisis') + log_incident(severity='HIGH')
- MEDIUM: get_crisis_resources(situation_type='support') + log_incident(severity='MEDIUM')
- LOW: No tool calls (false positive / everyday situations)

This approach:
- Model learns consistent "if not LOW, call tools" pattern
- Tool parameters encode severity level
- Region-agnostic from day one

Usage:
    python normalize_training_data.py input.jsonl output.jsonl [--dry-run]
"""

import json
import re
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


# Tool call templates
TOOL_TEMPLATES = {
    "get_crisis_resources": "[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='{situation}')]",
    "log_incident": "[TOOL_CALL: log_incident(incident_data={{'type': '{incident_type}', 'severity': '{severity}'}})]",
}

# Map patterns to situation types for get_crisis_resources
SITUATION_TYPE_MAP = {
    "suicide": ["suicid", "kill.*self", "end.*life", "death wish", "pills", "overdose", "jump", "hang"],
    "self_harm": ["self.?harm", "cut.*self", "hurt.*self", "burn.*self"],
    "domestic_violence": ["hit.*me", "abuse", "violent", "partner.*hurt", "dv", "domestic", "refuge"],
    "psychosis": ["voices", "command", "psycho", "hallucin", "delusion"],
    "substance_abuse": ["drug", "alcohol", "relapse", "using again", "overdose"],
    "youth": ["school", "bully", "ncea", "parent", "teen"],
    "mental_health": [],  # Default fallback
}


def extract_risk_level(output: str) -> str:
    """Extract risk level from output text."""
    match = re.search(r'RISK LEVEL:\s*(\w+)', output, re.IGNORECASE)
    if match:
        level = match.group(1).upper()
        if level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            return level

    # Fallback: check for level keywords
    output_upper = output.upper()
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if level in output_upper:
            return level

    return "MEDIUM"  # Default


def extract_categories(instruction: str, output: str) -> List[str]:
    """Extract crisis categories from the example."""
    categories = []
    combined = (instruction + " " + output).lower()

    category_patterns = {
        "suicide_ideation": r'suicid|death.?wish|end.*life|kill.*self|not.*here|better.*without',
        "self_harm": r'self.?harm|cut.*self|hurt.*self|burn.*self',
        "domestic_violence": r'domestic|dv|hit.*me|partner.*abus|violent.*relationship|refuge|coercive',
        "child_abuse": r'child.*abuse|touch.*inapprop|oranga.?tamariki',
        "substance_abuse": r'drug|alcohol|relapse|overdose|substance|using.*again',
        "eating_disorder": r'eating|anorex|bulim|purge|starv.*self',
        "psychotic_symptoms": r'voices|command|psycho|hallucin|delusion',
        "youth_specific": r'school|bully|ncea|teen|youth',
        "has_plan": r'plan|going to|will.*tonight|ready to',
        "has_means": r'pills|gun|rope|knife|bridge|means',
        "imminent": r'tonight|right now|about to|ready',
    }

    for category, pattern in category_patterns.items():
        if re.search(pattern, combined):
            categories.append(category)

    return categories


def detect_situation_type(instruction: str, output: str) -> str:
    """Detect the appropriate situation type for get_crisis_resources."""
    combined = (instruction + " " + output).lower()

    for situation, patterns in SITUATION_TYPE_MAP.items():
        for pattern in patterns:
            if re.search(pattern, combined):
                return situation

    return "mental_health"  # Default


def detect_incident_type(instruction: str, output: str) -> str:
    """Detect incident type for log_incident."""
    combined = (instruction + " " + output).lower()

    if re.search(r'suicid|kill.*self|end.*life', combined):
        if re.search(r'plan|means|pills|gun|rope', combined):
            return "suicide_plan_with_means"
        return "suicide_ideation"
    elif re.search(r'self.?harm', combined):
        return "self_harm"
    elif re.search(r'domestic|hit.*me|abus.*partner|violent.*relation', combined):
        return "domestic_violence"
    elif re.search(r'voices|command|psycho', combined):
        return "psychosis"
    elif re.search(r'drug|alcohol|relapse|overdose', combined):
        return "substance_crisis"
    elif re.search(r'hopeless|trapped|spiral', combined):
        return "mental_health_crisis"

    return "crisis_detected"


def has_tool_call(output: str, tool_name: str) -> bool:
    """Check if output contains a specific tool call."""
    return tool_name in output and "[TOOL_CALL:" in output


def remove_tool_calls(output: str) -> str:
    """Remove all tool calls from output."""
    # Remove [TOOL_CALL: ...] patterns
    cleaned = re.sub(r'\[TOOL_CALL:[^\]]+\]\n*', '', output)
    # Clean up extra newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def get_situation_type_for_risk(risk_level: str, detected_situation: str) -> str:
    """Map risk level to appropriate situation_type for get_crisis_resources."""
    if risk_level == "CRITICAL":
        return "emergency"
    elif risk_level == "HIGH":
        return "crisis"
    elif risk_level == "MEDIUM":
        return "support"
    return detected_situation


def add_tool_calls(output: str, risk_level: str, situation_type: str, incident_type: str) -> str:
    """Add appropriate tool calls to output based on risk level.

    Policy (Option B):
    - CRITICAL: emergency situation tools
    - HIGH: crisis situation tools
    - MEDIUM: support situation tools
    - LOW: no tools
    """
    if risk_level == "LOW":
        return output  # LOW never gets tools

    # Map risk level to situation type
    mapped_situation = get_situation_type_for_risk(risk_level, situation_type)

    # Check what's already there
    has_get_resources = has_tool_call(output, "get_crisis_resources")
    has_log_incident = has_tool_call(output, "log_incident")

    tools_to_add = []

    if not has_get_resources:
        tools_to_add.append(
            TOOL_TEMPLATES["get_crisis_resources"].format(situation=mapped_situation)
        )

    if not has_log_incident:
        tools_to_add.append(
            TOOL_TEMPLATES["log_incident"].format(
                incident_type=incident_type,
                severity=risk_level
            )
        )

    if not tools_to_add:
        return output  # Already has both

    # Find insertion point (after ACTION: line or after PATTERNS DETECTED:)
    lines = output.split('\n')
    insert_idx = None

    for i, line in enumerate(lines):
        if line.startswith("ACTION:") or line.startswith("PATTERNS DETECTED:"):
            insert_idx = i + 1
            break

    if insert_idx is None:
        # Fallback: insert after first line
        insert_idx = 1

    # Insert tool calls
    tool_block = '\n' + '\n'.join(tools_to_add) + '\n'
    lines.insert(insert_idx, tool_block)

    return '\n'.join(lines)


def normalize_output_structure(output: str, risk_level: str) -> str:
    """Ensure consistent output structure."""
    # Ensure RISK LEVEL is at the start
    if not output.strip().startswith("RISK LEVEL:"):
        # Try to find and move it
        match = re.search(r'(RISK LEVEL:\s*\w+[^\n]*)', output)
        if match:
            risk_line = match.group(1)
            output = re.sub(r'RISK LEVEL:\s*\w+[^\n]*\n?', '', output)
            output = risk_line + '\n' + output.strip()
        else:
            # Add it
            output = f"RISK LEVEL: {risk_level}\n" + output.strip()

    return output


def normalize_example(example: Dict) -> Tuple[Dict, Dict]:
    """
    Normalize a single training example.

    Returns:
        Tuple of (normalized_example, changes_made)
    """
    instruction = example.get("instruction", "")
    output = example.get("output", "")

    changes = {
        "risk_level_extracted": False,
        "tools_added": False,
        "tools_removed": False,
        "structure_fixed": False,
        "metadata_added": False,
    }

    # Extract risk level
    risk_level = extract_risk_level(output)
    changes["risk_level_extracted"] = True

    # Extract categories
    categories = extract_categories(instruction, output)

    # Detect situation and incident types
    situation_type = detect_situation_type(instruction, output)
    incident_type = detect_incident_type(instruction, output)

    original_output = output

    # Apply policy based on risk level (Option B)
    if risk_level in ["CRITICAL", "HIGH", "MEDIUM"]:
        # Ensure tool calls are present with appropriate situation_type
        output = add_tool_calls(output, risk_level, situation_type, incident_type)
        if output != original_output:
            changes["tools_added"] = True

    elif risk_level == "LOW":
        # Remove any tool calls (false positives shouldn't trigger tools)
        new_output = remove_tool_calls(output)
        if new_output != output:
            output = new_output
            changes["tools_removed"] = True

    # Normalize structure
    output = normalize_output_structure(output, risk_level)
    if output != original_output and not changes["tools_added"] and not changes["tools_removed"]:
        changes["structure_fixed"] = True

    # Build normalized example with metadata
    normalized = {
        "instruction": instruction,
        "input": example.get("input", ""),
        "output": output,
        # Metadata for training framework
        "risk_level": risk_level,
        "categories": categories,
        "situation_type": situation_type,
    }

    changes["metadata_added"] = True

    return normalized, changes


def analyze_dataset(examples: List[Dict]) -> Dict:
    """Analyze dataset before normalization."""
    stats = defaultdict(lambda: {
        "total": 0,
        "has_any_tool": 0,
        "has_get_resources": 0,
        "has_log_incident": 0,
    })

    for ex in examples:
        output = ex.get("output", "")
        risk_level = extract_risk_level(output)

        stats[risk_level]["total"] += 1
        if "[TOOL_CALL:" in output:
            stats[risk_level]["has_any_tool"] += 1
        if "get_crisis_resources" in output:
            stats[risk_level]["has_get_resources"] += 1
        if "log_incident" in output:
            stats[risk_level]["has_log_incident"] += 1

    return dict(stats)


def print_stats(stats: Dict, title: str):
    """Print statistics table."""
    print(f"\n{title}")
    print("=" * 70)
    print(f"{'Risk Level':<12} {'Total':<8} {'Any Tool':<12} {'get_resources':<15} {'log_incident':<12}")
    print("-" * 70)

    for risk in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        s = stats.get(risk, {"total": 0, "has_any_tool": 0, "has_get_resources": 0, "has_log_incident": 0})
        if s["total"] > 0:
            any_pct = s["has_any_tool"] / s["total"] * 100
            get_pct = s["has_get_resources"] / s["total"] * 100
            log_pct = s["has_log_incident"] / s["total"] * 100
            print(f"{risk:<12} {s['total']:<8} {any_pct:>5.1f}%      {get_pct:>5.1f}%          {log_pct:>5.1f}%")

    print("-" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Normalize Guardian training data for consistent tool calling"
    )
    parser.add_argument("input_file", help="Input JSONL file")
    parser.add_argument("output_file", help="Output JSONL file")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, don't write")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed changes")

    args = parser.parse_args()

    # Load input data
    print(f"Loading {args.input_file}...")
    examples = []
    with open(args.input_file, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line.strip()))

    print(f"Loaded {len(examples)} examples")

    # Analyze before
    before_stats = analyze_dataset(examples)
    print_stats(before_stats, "BEFORE NORMALIZATION")

    if args.dry_run:
        print("\n[DRY RUN] No changes written")
        return

    # Normalize
    print("\nNormalizing...")
    normalized_examples = []
    total_changes = defaultdict(int)

    for i, example in enumerate(examples):
        normalized, changes = normalize_example(example)
        normalized_examples.append(normalized)

        for change_type, occurred in changes.items():
            if occurred:
                total_changes[change_type] += 1

        if args.verbose and any([changes["tools_added"], changes["tools_removed"]]):
            risk = normalized["risk_level"]
            print(f"  [{i}] {risk}: {'added tools' if changes['tools_added'] else 'removed tools'}")

    # Analyze after
    after_stats = analyze_dataset(normalized_examples)
    print_stats(after_stats, "AFTER NORMALIZATION")

    # Summary of changes
    print("\nCHANGES MADE")
    print("-" * 40)
    print(f"  Tools added:    {total_changes['tools_added']}")
    print(f"  Tools removed:  {total_changes['tools_removed']}")
    print(f"  Structure fixed: {total_changes['structure_fixed']}")
    print(f"  Metadata added: {total_changes['metadata_added']}")

    # Write output
    print(f"\nWriting to {args.output_file}...")
    with open(args.output_file, 'w', encoding='utf-8') as f:
        for example in normalized_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"Done! Normalized {len(normalized_examples)} examples")

    # Recommendations
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print(f"1. Review output: head -5 {args.output_file} | python -m json.tool")
    print(f"2. Train with: python train_guardian_llm.py --training-file {args.output_file}")
    print("3. The metadata fields (risk_level, categories) enable automatic weighting")


if __name__ == "__main__":
    main()
