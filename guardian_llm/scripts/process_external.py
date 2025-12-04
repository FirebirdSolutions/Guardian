#!/usr/bin/env python3
"""
Process external mental health datasets into Guardian training format.

Supports:
- Mendeley Suicide Reddit Dataset (CSV)
- SWMH Dataset from Hugging Face (various formats)

Usage:
    python -m guardian_llm.scripts.process_external mendeley <input_file> <output_file>
    python -m guardian_llm.scripts.process_external swmh <input_dir> <output_file>
"""

import json
import csv
import re
import sys
import random
from pathlib import Path
from typing import Dict, List, Tuple

from guardian_llm.data_utils import INSTRUCTION_TEMPLATE_V2

# Global instruction template (region-agnostic)
INSTRUCTION_TEMPLATE_GLOBAL = """You are Guardian, an AI crisis detection system.

Your role:
- Analyze messages for crisis indicators (mental health, domestic violence, self-harm, etc.)
- Classify risk level: CRITICAL, HIGH, MEDIUM, or LOW
- For CRITICAL/HIGH/MEDIUM: Use tool calls to get verified crisis resources
- Never hallucinate resources - always use get_crisis_resources() tool
- Respond with empathy and accuracy

Analyze this message:
User: '{user_message}'"""


# Output templates by risk level
OUTPUT_TEMPLATES = {
    "CRITICAL": [
        """RISK LEVEL: CRITICAL
PATTERNS DETECTED: {patterns}
ACTION: IMMEDIATE emergency intervention

[TOOL_CALL: get_crisis_resources(region='GLOBAL', situation_type='emergency')]

INTERVENTION:
- Emergency services (local emergency number)
- Crisis line (local crisis line)

ESCALATE: CRITICAL - Immediate risk detected""",
    ],
    "HIGH": [
        """RISK LEVEL: HIGH
PATTERNS DETECTED: {patterns}
ACTION: Provide crisis resources

[TOOL_CALL: get_crisis_resources(region='GLOBAL', situation_type='crisis')]

INTERVENTION:
- Crisis line available 24/7
- Mental health support services

NOTE: Elevated risk - monitor closely""",
    ],
    "MEDIUM": [
        """RISK LEVEL: MEDIUM
PATTERNS DETECTED: {patterns}
ACTION: Support resources available

[TOOL_CALL: get_crisis_resources(region='GLOBAL', situation_type='support')]

RESOURCES:
- Mental health support line if needed
- GP/healthcare provider for ongoing support

NOTE: Monitor for escalation""",
    ],
    "LOW": [
        """RISK LEVEL: LOW
PATTERNS DETECTED: {patterns}
ACTION: No immediate intervention needed

NOTE: Continue monitoring""",
    ],
}


def clean_text(text: str) -> str:
    """Clean text for training data."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '[URL]', text)
    # Remove Reddit-specific formatting
    text = re.sub(r'\[deleted\]|\[removed\]', '', text)
    # Truncate very long texts
    if len(text) > 500:
        text = text[:500] + '...'
    return text


def detect_patterns(text: str, is_crisis: bool) -> str:
    """Detect crisis patterns in text."""
    text_lower = text.lower()
    patterns = []

    # Suicide-related
    if any(w in text_lower for w in ['suicide', 'kill myself', 'end my life', 'want to die', 'don\'t want to live']):
        patterns.append('suicidal ideation')
    if any(w in text_lower for w in ['method', 'pills', 'gun', 'bridge', 'overdose', 'hanging']):
        patterns.append('method mentioned')
    if any(w in text_lower for w in ['tonight', 'today', 'now', 'ready', 'decided']):
        patterns.append('timeframe indicated')

    # Self-harm
    if any(w in text_lower for w in ['cut myself', 'cutting', 'self harm', 'hurt myself', 'blade']):
        patterns.append('self-harm')

    # Depression
    if any(w in text_lower for w in ['depressed', 'depression', 'hopeless', 'worthless', 'empty']):
        patterns.append('depression indicators')

    # Anxiety
    if any(w in text_lower for w in ['anxiety', 'panic', 'anxious', 'scared', 'terrified']):
        patterns.append('anxiety indicators')

    # Isolation
    if any(w in text_lower for w in ['alone', 'lonely', 'no one', 'nobody', 'isolated']):
        patterns.append('isolation')

    # Burden
    if any(w in text_lower for w in ['burden', 'better off without', 'everyone would be better']):
        patterns.append('perceived burdensomeness')

    if not patterns:
        if is_crisis:
            patterns.append('general distress')
        else:
            patterns.append('general discussion')

    return ', '.join(patterns)


def map_risk_level(label: str, text: str) -> str:
    """Map dataset labels to Guardian risk levels."""
    label_lower = label.lower()
    text_lower = text.lower()

    # Check for critical indicators in text regardless of label
    critical_phrases = [
        'going to kill', 'will kill myself', 'end it tonight', 'goodbye',
        'final goodbye', 'suicide note', 'already decided', 'have a plan',
        'method ready', 'pills ready', 'gun loaded'
    ]
    if any(phrase in text_lower for phrase in critical_phrases):
        return 'CRITICAL'

    # Map by label
    if label_lower in ['suicide', 'suicidal', '1', 'positive', 'high', 'severe']:
        # Check text for severity
        if any(w in text_lower for w in ['tonight', 'now', 'today', 'ready', 'decided', 'plan']):
            return 'CRITICAL'
        return 'HIGH'

    if label_lower in ['depression', 'anxiety', 'moderate', 'medium']:
        return 'MEDIUM' if 'severe' not in text_lower else 'HIGH'

    if label_lower in ['non-suicide', 'non-suicidal', '0', 'negative', 'low', 'none']:
        # Double-check the text doesn't contain crisis language
        if any(w in text_lower for w in ['kill myself', 'suicide', 'end my life']):
            return 'HIGH'  # Override label if text indicates risk
        return 'LOW'

    # Default based on text analysis
    if any(w in text_lower for w in ['hopeless', 'worthless', 'can\'t go on']):
        return 'HIGH'

    return 'MEDIUM'


def create_guardian_example(text: str, risk_level: str) -> Dict:
    """Create a Guardian training example from text and risk level."""
    cleaned_text = clean_text(text)
    if not cleaned_text or len(cleaned_text) < 10:
        return None

    patterns = detect_patterns(cleaned_text, risk_level in ['CRITICAL', 'HIGH'])
    template = random.choice(OUTPUT_TEMPLATES[risk_level])
    output = template.format(patterns=patterns)

    return {
        'instruction': INSTRUCTION_TEMPLATE_GLOBAL.format(user_message=cleaned_text),
        'input': '',
        'output': output
    }


def process_mendeley(input_file: Path, output_file: Path) -> Tuple[int, Dict]:
    """
    Process Mendeley Suicide Reddit Dataset.

    Expected format: CSV with columns like 'text' and 'class'/'label'
    """
    stats = {'total': 0, 'processed': 0, 'by_risk': {}}
    examples = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        # Try to detect CSV format
        sample = f.read(4096)
        f.seek(0)

        # Detect delimiter
        if '\t' in sample:
            reader = csv.DictReader(f, delimiter='\t')
        else:
            reader = csv.DictReader(f)

        # Find text and label columns
        fieldnames = reader.fieldnames
        text_col = None
        label_col = None

        for col in fieldnames:
            col_lower = col.lower()
            if 'text' in col_lower or 'post' in col_lower or 'content' in col_lower:
                text_col = col
            if 'class' in col_lower or 'label' in col_lower or 'suicide' in col_lower:
                label_col = col

        if not text_col:
            print(f"Could not find text column. Available: {fieldnames}")
            return 0, stats

        print(f"Using columns: text='{text_col}', label='{label_col}'")

        for row in reader:
            stats['total'] += 1

            text = row.get(text_col, '')
            label = row.get(label_col, 'unknown') if label_col else 'unknown'

            if not text or len(text.strip()) < 20:
                continue

            risk_level = map_risk_level(str(label), text)
            example = create_guardian_example(text, risk_level)

            if example:
                examples.append(example)
                stats['processed'] += 1
                stats['by_risk'][risk_level] = stats['by_risk'].get(risk_level, 0) + 1

    # Shuffle and write
    random.shuffle(examples)

    with open(output_file, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    return len(examples), stats


def process_swmh(input_dir: Path, output_file: Path) -> Tuple[int, Dict]:
    """
    Process SWMH Dataset from Hugging Face.

    Expected format: Directory with JSON/JSONL files
    """
    stats = {'total': 0, 'processed': 0, 'by_risk': {}}
    examples = []

    input_dir = Path(input_dir)

    # Find all JSON files
    json_files = list(input_dir.glob('**/*.json')) + list(input_dir.glob('**/*.jsonl'))

    if not json_files:
        # Maybe it's a single file
        if input_dir.suffix in ['.json', '.jsonl']:
            json_files = [input_dir]
        else:
            print(f"No JSON files found in {input_dir}")
            return 0, stats

    for json_file in json_files:
        print(f"Processing: {json_file}")

        with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
            # Try JSONL first
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        process_swmh_record(data, examples, stats)
                    except json.JSONDecodeError:
                        continue
            except:
                # Try as single JSON
                f.seek(0)
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            process_swmh_record(item, examples, stats)
                    else:
                        process_swmh_record(data, examples, stats)
                except:
                    print(f"Could not parse {json_file}")

    # Shuffle and write
    random.shuffle(examples)

    with open(output_file, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    return len(examples), stats


def process_swmh_record(data: Dict, examples: List, stats: Dict):
    """Process a single SWMH record."""
    stats['total'] += 1

    # Try to find text field
    text = (data.get('text') or data.get('post') or data.get('content') or
            data.get('body') or data.get('selftext') or '')

    if not text or len(text.strip()) < 20:
        return

    # Try to find label
    label = (data.get('label') or data.get('class') or data.get('subreddit') or
             data.get('category') or 'unknown')

    # Subreddit-based labeling
    if isinstance(label, str):
        if 'suicidewatch' in label.lower():
            label = 'suicide'
        elif 'depression' in label.lower():
            label = 'depression'
        elif 'anxiety' in label.lower():
            label = 'anxiety'

    risk_level = map_risk_level(str(label), text)
    example = create_guardian_example(text, risk_level)

    if example:
        examples.append(example)
        stats['processed'] += 1
        stats['by_risk'][risk_level] = stats['by_risk'].get(risk_level, 0) + 1


def process_generic_csv(input_file: Path, output_file: Path) -> Tuple[int, Dict]:
    """Process any CSV file with text and optional label columns."""
    return process_mendeley(input_file, output_file)


def main():
    if len(sys.argv) < 4:
        print("""
Process External Mental Health Datasets for Guardian

Usage:
    python -m guardian_llm.scripts.process_external <format> <input> <output>

Formats:
    mendeley    - Mendeley Suicide Reddit Dataset (CSV)
    swmh        - SWMH Dataset (JSON/JSONL directory or file)
    csv         - Generic CSV with text/label columns

Examples:
    python -m guardian_llm.scripts.process_external mendeley suicide_data.csv guardian_suicide.jsonl
    python -m guardian_llm.scripts.process_external swmh ./swmh_data/ guardian_swmh.jsonl
    python -m guardian_llm.scripts.process_external csv any_dataset.csv guardian_output.jsonl

Output:
    Creates JSONL file in Guardian V2 training format with:
    - Clean instruction template
    - Risk level classification
    - Tool calls for CRITICAL/HIGH/MEDIUM
    - Pattern detection
        """)
        sys.exit(1)

    format_type = sys.argv[1].lower()
    input_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    if not input_path.exists():
        print(f"Error: Input not found: {input_path}")
        sys.exit(1)

    print(f"Processing {format_type} dataset...")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print()

    if format_type == 'mendeley':
        count, stats = process_mendeley(input_path, output_path)
    elif format_type == 'swmh':
        count, stats = process_swmh(input_path, output_path)
    elif format_type == 'csv':
        count, stats = process_generic_csv(input_path, output_path)
    else:
        print(f"Unknown format: {format_type}")
        sys.exit(1)

    print(f"\nResults:")
    print(f"  Total records: {stats['total']}")
    print(f"  Processed: {stats['processed']}")
    print(f"  Output file: {output_path}")
    print(f"\nBy risk level:")
    for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = stats['by_risk'].get(level, 0)
        pct = (count / stats['processed'] * 100) if stats['processed'] > 0 else 0
        print(f"  {level}: {count} ({pct:.1f}%)")

    print(f"\nNext steps:")
    print(f"  1. Review samples: head -5 {output_path}")
    print(f"  2. Merge with training data:")
    print(f"     cat {output_path} >> 'guardian_llm/data/training-data-final.jsonl'")


if __name__ == '__main__':
    main()
