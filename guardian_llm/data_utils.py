"""
Guardian LLM Data Utilities

Consolidated utilities for building, converting, and generating training data.
All utilities use the clean V2 instruction format.

Functions:
- build_dataset: Combine modular components into training data
- split_dataset: Split training data into modular components for editing
- convert_format: Convert between training formats (Alpaca, ChatML, Llama, etc.)
- prepare_batch_requests: Create Anthropic batch API requests for data generation
- process_batch_results: Process batch API results into training data
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Constants and Templates
# =============================================================================

# The clean V2 instruction template (NO hardcoded resources)
INSTRUCTION_TEMPLATE_V2 = """You are Guardian, an AI crisis detection system for New Zealand.

Your role:
- Analyze messages for crisis indicators (mental health, domestic violence, self-harm, etc.)
- Classify risk level: CRITICAL, HIGH, MEDIUM, or LOW
- For CRITICAL/HIGH/MEDIUM: Use tool calls to get verified crisis resources
- Never hallucinate resources - always use get_crisis_resources() tool
- Respond with empathy and accuracy

Analyze this message:
User: '{user_message}'"""


class TrainingFormat(Enum):
    """Supported training data formats."""
    ALPACA = "alpaca"
    CHATML = "chatml"
    OPENAI = "openai"
    LLAMA = "llama"
    MISTRAL = "mistral"
    QWEN = "qwen"


@dataclass
class DatasetStats:
    """Statistics about a training dataset."""
    total: int = 0
    by_risk_level: Dict[str, int] = field(default_factory=dict)
    with_tool_calls: int = 0
    without_tool_calls: int = 0
    avg_instruction_length: float = 0.0
    avg_output_length: float = 0.0


# =============================================================================
# Format Conversion
# =============================================================================

def to_alpaca_format(instruction: str, output: str, input_text: str = "") -> Dict:
    """Convert to Alpaca/Instruction format."""
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output
    }


def to_chatml_format(instruction: str, output: str) -> Dict:
    """Convert to ChatML conversational format."""
    return {
        "messages": [
            {"role": "system", "content": "You are Guardian, an AI crisis detection system."},
            {"role": "user", "content": instruction},
            {"role": "assistant", "content": output}
        ]
    }


def to_openai_format(instruction: str, output: str) -> Dict:
    """Convert to OpenAI fine-tuning format."""
    # Extract just the user message for cleaner format
    user_msg = extract_user_message(instruction) or instruction
    return {
        "messages": [
            {"role": "system", "content": "You are Guardian, an AI crisis detection system for New Zealand. Analyze messages for crisis indicators, classify risk levels, and use tool calls to get verified crisis resources. Never hallucinate resources."},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": output}
        ]
    }


def to_llama_format(instruction: str, output: str) -> Dict:
    """Convert to Llama prompt format."""
    return {
        "text": f"<s>[INST] <<SYS>>\nYou are Guardian, an AI crisis detection system.\n<</SYS>>\n\n{instruction} [/INST] {output} </s>"
    }


def to_mistral_format(instruction: str, output: str) -> Dict:
    """Convert to Mistral prompt format."""
    return {
        "text": f"[INST] {instruction} [/INST]{output}</s>"
    }


def to_qwen_format(instruction: str, output: str) -> Dict:
    """Convert to Qwen chat format."""
    return {
        "text": f"<|im_start|>system\nYou are Guardian, an AI crisis detection system.<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"
    }


FORMAT_CONVERTERS = {
    TrainingFormat.ALPACA: lambda i, o: to_alpaca_format(i, o),
    TrainingFormat.CHATML: to_chatml_format,
    TrainingFormat.OPENAI: to_openai_format,
    TrainingFormat.LLAMA: to_llama_format,
    TrainingFormat.MISTRAL: to_mistral_format,
    TrainingFormat.QWEN: to_qwen_format,
}


# =============================================================================
# Helper Functions
# =============================================================================

def extract_user_message(instruction: str) -> Optional[str]:
    """Extract the user message from an instruction string."""
    # Pattern: User: 'message' or User: "message"
    match = re.search(r"User:\s*['\"](.+?)['\"]$", instruction, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_risk_level(output: str) -> str:
    """Extract risk level from output text."""
    match = re.search(r'RISK LEVEL:\s*(\w+)', output, re.IGNORECASE)
    if match:
        level = match.group(1).upper()
        if level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            return level
    return "UNKNOWN"


def has_tool_call(output: str) -> bool:
    """Check if output contains a tool call."""
    return '[TOOL_CALL:' in output


def get_situation_type(risk_level: str) -> str:
    """Map risk level to situation type for tool calls."""
    mapping = {
        'CRITICAL': 'emergency',
        'HIGH': 'crisis',
        'MEDIUM': 'support'
    }
    return mapping.get(risk_level, 'support')


def categorize_output(output: str) -> Dict[str, Any]:
    """Categorize output by risk level and situation type."""
    category = {
        'risk_level': extract_risk_level(output),
        'situation_type': 'general',
        'patterns': [],
        'has_tool_call': has_tool_call(output)
    }

    # Extract patterns
    patterns_match = re.search(r'PATTERNS DETECTED:\s*([^\n]+)', output, re.IGNORECASE)
    if patterns_match:
        category['patterns'] = [p.strip() for p in patterns_match.group(1).split(',')]

    # Determine situation type from content
    output_lower = output.lower()
    if 'suicide' in output_lower or 'kill myself' in output_lower:
        category['situation_type'] = 'suicide'
    elif 'self-harm' in output_lower or 'self harm' in output_lower:
        category['situation_type'] = 'self_harm'
    elif 'domestic violence' in output_lower or 'family violence' in output_lower:
        category['situation_type'] = 'domestic_violence'
    elif 'child abuse' in output_lower or 'child protection' in output_lower:
        category['situation_type'] = 'child_abuse'
    elif 'psychotic' in output_lower or 'psychosis' in output_lower:
        category['situation_type'] = 'psychosis'
    elif 'substance' in output_lower or 'relapse' in output_lower:
        category['situation_type'] = 'substance_abuse'
    elif 'stalking' in output_lower or 'harassment' in output_lower:
        category['situation_type'] = 'stalking'
    elif 'mental health' in output_lower:
        category['situation_type'] = 'mental_health'

    return category


def compute_stats(examples: List[Dict]) -> DatasetStats:
    """Compute statistics for a list of training examples."""
    stats = DatasetStats()
    stats.total = len(examples)

    total_instruction_len = 0
    total_output_len = 0

    for ex in examples:
        instruction = ex.get('instruction', '')
        output = ex.get('output', '')

        total_instruction_len += len(instruction)
        total_output_len += len(output)

        risk = extract_risk_level(output)
        stats.by_risk_level[risk] = stats.by_risk_level.get(risk, 0) + 1

        if has_tool_call(output):
            stats.with_tool_calls += 1
        else:
            stats.without_tool_calls += 1

    if stats.total > 0:
        stats.avg_instruction_length = total_instruction_len / stats.total
        stats.avg_output_length = total_output_len / stats.total

    return stats


# =============================================================================
# Build Dataset from Components
# =============================================================================

def build_dataset(
    prompts: List[Dict],
    outputs: Dict[str, str],
    instruction_template: str = INSTRUCTION_TEMPLATE_V2
) -> List[Dict]:
    """
    Build training dataset from modular components.

    Args:
        prompts: List of prompt dicts with 'text' and 'output_id' keys
        outputs: Dict mapping output_id to output text
        instruction_template: Template with {user_message} placeholder

    Returns:
        List of training examples in Alpaca format
    """
    examples = []

    for prompt in prompts:
        user_message = prompt.get('text', '')
        output_id = prompt.get('output_id', '')

        output_text = outputs.get(output_id)
        if not output_text:
            logger.warning(f"Missing output for {output_id}")
            continue

        instruction = instruction_template.format(user_message=user_message)

        examples.append({
            'instruction': instruction,
            'input': '',
            'output': output_text
        })

    return examples


def build_dataset_from_files(
    prompts_file: Path,
    outputs_file: Path,
    output_path: Path,
    instruction_template: str = INSTRUCTION_TEMPLATE_V2
) -> Tuple[int, DatasetStats]:
    """
    Build training dataset from component files.

    Args:
        prompts_file: JSONL file with prompts
        outputs_file: JSONL file with outputs
        output_path: Path for output JSONL file
        instruction_template: Instruction template to use

    Returns:
        Tuple of (count, stats)
    """
    # Load prompts
    prompts = []
    with open(prompts_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                prompts.append(json.loads(line))

    # Load outputs
    outputs = {}
    with open(outputs_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                out = json.loads(line)
                outputs[out['id']] = out['text']

    # Build dataset
    examples = build_dataset(prompts, outputs, instruction_template)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    stats = compute_stats(examples)
    return len(examples), stats


# =============================================================================
# Split Dataset into Components
# =============================================================================

def split_dataset_to_components(
    input_file: Path,
    output_dir: Path
) -> Dict[str, int]:
    """
    Split training dataset into modular components for editing.

    Creates:
    - prompts.jsonl: User messages with IDs
    - outputs.jsonl: Outputs with IDs and categories
    - categories.json: Summary of output categories

    Args:
        input_file: Input JSONL training file
        output_dir: Directory for output files

    Returns:
        Dict with counts
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    prompts = []
    outputs = []
    categories_summary = {}

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
                instruction = entry.get('instruction', '')
                output = entry.get('output', '')

                # Extract user message
                user_message = extract_user_message(instruction) or instruction

                # Categorize output
                category = categorize_output(output)

                # Create IDs
                prompt_id = f'prompt_{line_num}'
                output_id = f'output_{line_num}'

                prompts.append({
                    'id': prompt_id,
                    'text': user_message,
                    'output_id': output_id
                })

                outputs.append({
                    'id': output_id,
                    'text': output,
                    'risk_level': category['risk_level'],
                    'situation_type': category['situation_type'],
                    'has_tool_call': category['has_tool_call']
                })

                # Track categories
                sit_type = category['situation_type']
                if sit_type not in categories_summary:
                    categories_summary[sit_type] = {'count': 0, 'risk_levels': {}}
                categories_summary[sit_type]['count'] += 1

                risk = category['risk_level']
                if risk not in categories_summary[sit_type]['risk_levels']:
                    categories_summary[sit_type]['risk_levels'][risk] = 0
                categories_summary[sit_type]['risk_levels'][risk] += 1

            except Exception as e:
                logger.warning(f"Error on line {line_num}: {e}")

    # Write prompts
    with open(output_dir / 'prompts.jsonl', 'w', encoding='utf-8') as f:
        for p in prompts:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')

    # Write outputs
    with open(output_dir / 'outputs.jsonl', 'w', encoding='utf-8') as f:
        for o in outputs:
            f.write(json.dumps(o, ensure_ascii=False) + '\n')

    # Write categories summary
    with open(output_dir / 'categories.json', 'w', encoding='utf-8') as f:
        json.dump(categories_summary, f, indent=2)

    return {
        'prompts': len(prompts),
        'outputs': len(outputs),
        'categories': len(categories_summary)
    }


# =============================================================================
# Convert Between Formats
# =============================================================================

def convert_format(
    input_file: Path,
    output_file: Path,
    target_format: TrainingFormat = TrainingFormat.ALPACA,
    source_format: str = "alpaca"
) -> Tuple[int, int]:
    """
    Convert training data between formats.

    Args:
        input_file: Input JSONL file
        output_file: Output JSONL file
        target_format: Target format enum
        source_format: Source format ("alpaca", "chatml", or "prompt_response")

    Returns:
        Tuple of (converted_count, skipped_count)
    """
    converter = FORMAT_CONVERTERS.get(target_format)
    if not converter:
        raise ValueError(f"Unknown format: {target_format}")

    converted = 0
    skipped = 0

    with open(input_file, 'r', encoding='utf-8') as inf, \
         open(output_file, 'w', encoding='utf-8') as outf:

        for line in inf:
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)

                # Extract instruction and output based on source format
                if source_format == "alpaca":
                    instruction = record.get('instruction', '')
                    output = record.get('output', '')
                elif source_format == "chatml":
                    messages = record.get('messages', [])
                    instruction = next((m['content'] for m in messages if m['role'] == 'user'), '')
                    output = next((m['content'] for m in messages if m['role'] == 'assistant'), '')
                elif source_format == "prompt_response":
                    instruction = record.get('prompt', '')
                    output = record.get('response', '')
                else:
                    instruction = record.get('instruction', record.get('prompt', ''))
                    output = record.get('output', record.get('response', ''))

                if not instruction or not output:
                    skipped += 1
                    continue

                # Convert to target format
                converted_record = converter(instruction, output)
                outf.write(json.dumps(converted_record, ensure_ascii=False) + '\n')
                converted += 1

            except Exception as e:
                logger.warning(f"Error converting record: {e}")
                skipped += 1

    return converted, skipped


# =============================================================================
# Batch API Integration (Anthropic)
# =============================================================================

BATCH_GENERATION_PROMPT = """You are helping create training data for Guardian, an AI crisis detection system.

Given a seed message, generate 3 variations with appropriate Guardian responses.

Guidelines:
- Vary the phrasing, intensity, and context of the message
- Responses must include:
  - RISK LEVEL: CRITICAL, HIGH, MEDIUM, or LOW
  - PATTERNS DETECTED: what crisis indicators were found
  - For CRITICAL/HIGH/MEDIUM: [TOOL_CALL: get_crisis_resources(region='NZ', situation_type='X')]
  - INTERVENTION: Verified resources (111, 1737, etc.)
- Never invent fake phone numbers or resources
- Use NZ resources: 111 (emergency), 1737 (crisis line), 0800 543 354 (Lifeline)

Seed message: "{seed_message}"
Risk level hint: {risk_level}

Respond with JSON:
{{
  "variations": [
    {{"user_message": "...", "output": "..."}},
    {{"user_message": "...", "output": "..."}},
    {{"user_message": "...", "output": "..."}}
  ]
}}"""


def prepare_batch_requests(
    seed_examples: List[Dict],
    output_file: Path,
    model: str = "claude-sonnet-4-20250514"
) -> int:
    """
    Prepare batch requests for Anthropic API to generate training data variations.

    Args:
        seed_examples: List of seed examples with 'user_message' and 'risk_level'
        output_file: Output JSONL file for batch requests
        model: Claude model to use

    Returns:
        Number of requests created
    """
    requests = []

    for i, seed in enumerate(seed_examples):
        user_message = seed.get('user_message', seed.get('text', ''))
        risk_level = seed.get('risk_level', 'HIGH')

        prompt = BATCH_GENERATION_PROMPT.format(
            seed_message=user_message,
            risk_level=risk_level
        )

        request = {
            "custom_id": f"guardian_gen_{i}",
            "params": {
                "model": model,
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            }
        }
        requests.append(request)

    with open(output_file, 'w', encoding='utf-8') as f:
        for req in requests:
            f.write(json.dumps(req) + '\n')

    return len(requests)


def process_batch_results(
    results_file: Path,
    output_file: Path,
    instruction_template: str = INSTRUCTION_TEMPLATE_V2
) -> Tuple[int, int]:
    """
    Process Anthropic batch API results into training data.

    Args:
        results_file: JSONL file with batch results
        output_file: Output JSONL file for training data
        instruction_template: Instruction template to use

    Returns:
        Tuple of (created_count, error_count)
    """
    training_entries = []
    errors = 0

    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line)
            custom_id = result.get("custom_id", "unknown")

            try:
                # Handle both raw and processed result formats
                if "result" in result:
                    if isinstance(result["result"], dict):
                        content = result["result"]["message"]["content"][0]["text"]
                    else:
                        content = result["result"].message.content[0].text
                else:
                    content = result.get("content", "")

                # Parse JSON response
                variations = json.loads(content)

                for var in variations.get("variations", []):
                    user_msg = var.get("user_message", "")
                    output = var.get("output", "")

                    if user_msg and output:
                        instruction = instruction_template.format(user_message=user_msg)
                        training_entries.append({
                            "instruction": instruction,
                            "input": "",
                            "output": output
                        })

            except Exception as e:
                logger.warning(f"{custom_id}: {e}")
                errors += 1

    # Write training file
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in training_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    return len(training_entries), errors


# =============================================================================
# Normalize/Prepare Dataset (combines format + tool calling fixes)
# =============================================================================

def normalize_dataset(
    input_file: Path,
    output_file: Path,
    instruction_template: str = INSTRUCTION_TEMPLATE_V2,
    ensure_tool_calls: bool = True
) -> Dict[str, int]:
    """
    Normalize dataset with clean format and consistent tool calling.

    This is the recommended way to prepare training data.

    Args:
        input_file: Input JSONL file (any format)
        output_file: Output JSONL file
        instruction_template: Instruction template to use
        ensure_tool_calls: Whether to add/remove tool calls based on risk level

    Returns:
        Dict with stats
    """
    stats = {
        'total': 0,
        'processed': 0,
        'tools_added': 0,
        'tools_removed': 0,
        'by_risk': {}
    }

    examples = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            stats['total'] += 1

            try:
                original = json.loads(line)
                instruction = original.get('instruction', '')
                output = original.get('output', '')

                # Extract user message
                user_message = extract_user_message(instruction) or instruction

                # Create clean instruction
                clean_instruction = instruction_template.format(user_message=user_message)

                # Extract risk level
                risk_level = extract_risk_level(output)
                stats['by_risk'][risk_level] = stats['by_risk'].get(risk_level, 0) + 1

                # Handle tool calls if needed
                if ensure_tool_calls:
                    original_has_tool = has_tool_call(output)

                    if risk_level in ['CRITICAL', 'HIGH', 'MEDIUM'] and not original_has_tool:
                        # Add tool call
                        situation_type = get_situation_type(risk_level)
                        tool_call = f"\n\n[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='{situation_type}')]"

                        # Insert after ACTION line or at start
                        if 'ACTION:' in output:
                            parts = output.split('\n')
                            for i, part in enumerate(parts):
                                if part.startswith('ACTION:'):
                                    parts.insert(i + 1, tool_call.strip())
                                    break
                            output = '\n'.join(parts)
                        else:
                            lines = output.split('\n')
                            lines.insert(1, tool_call.strip())
                            output = '\n'.join(lines)

                        stats['tools_added'] += 1

                    elif risk_level == 'LOW' and original_has_tool:
                        # Remove tool calls
                        output = re.sub(r'\n*\[TOOL_CALL:[^\]]+\]', '', output)
                        stats['tools_removed'] += 1

                # Clean up
                output = re.sub(r'\n{3,}', '\n\n', output).strip()

                examples.append({
                    'instruction': clean_instruction,
                    'input': '',
                    'output': output
                })
                stats['processed'] += 1

            except Exception as e:
                logger.warning(f"Error: {e}")

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    return stats


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Command-line interface for data utilities."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Guardian LLM Data Utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  normalize   Normalize dataset with clean format + consistent tool calls
  convert     Convert between training formats
  split       Split dataset into modular components
  build       Build dataset from modular components
  stats       Show dataset statistics

Examples:
  # Normalize training data (recommended)
  python -m guardian_llm.data_utils normalize input.jsonl output.jsonl

  # Convert to Qwen format
  python -m guardian_llm.data_utils convert input.jsonl output.jsonl --format qwen

  # Show statistics
  python -m guardian_llm.data_utils stats training-data.jsonl
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Normalize command
    norm_parser = subparsers.add_parser('normalize', help='Normalize dataset')
    norm_parser.add_argument('input', help='Input JSONL file')
    norm_parser.add_argument('output', help='Output JSONL file')
    norm_parser.add_argument('--no-tool-fix', action='store_true', help='Skip tool call normalization')

    # Convert command
    conv_parser = subparsers.add_parser('convert', help='Convert format')
    conv_parser.add_argument('input', help='Input JSONL file')
    conv_parser.add_argument('output', help='Output JSONL file')
    conv_parser.add_argument('--format', choices=['alpaca', 'chatml', 'openai', 'llama', 'mistral', 'qwen'],
                            default='alpaca', help='Target format')
    conv_parser.add_argument('--source', default='alpaca', help='Source format')

    # Split command
    split_parser = subparsers.add_parser('split', help='Split into components')
    split_parser.add_argument('input', help='Input JSONL file')
    split_parser.add_argument('output_dir', help='Output directory')

    # Build command
    build_parser = subparsers.add_parser('build', help='Build from components')
    build_parser.add_argument('prompts', help='Prompts JSONL file')
    build_parser.add_argument('outputs', help='Outputs JSONL file')
    build_parser.add_argument('output', help='Output JSONL file')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('input', help='Input JSONL file')

    args = parser.parse_args()

    if args.command == 'normalize':
        print(f"Normalizing {args.input} -> {args.output}")
        stats = normalize_dataset(
            Path(args.input),
            Path(args.output),
            ensure_tool_calls=not args.no_tool_fix
        )
        print(f"\nResults:")
        print(f"  Total: {stats['total']}")
        print(f"  Processed: {stats['processed']}")
        print(f"  Tools added: {stats['tools_added']}")
        print(f"  Tools removed: {stats['tools_removed']}")
        print(f"\nBy risk level:")
        for risk, count in sorted(stats['by_risk'].items()):
            print(f"  {risk}: {count}")

    elif args.command == 'convert':
        print(f"Converting {args.input} -> {args.output} (format: {args.format})")
        target = TrainingFormat(args.format)
        converted, skipped = convert_format(Path(args.input), Path(args.output), target, args.source)
        print(f"Converted: {converted}, Skipped: {skipped}")

    elif args.command == 'split':
        print(f"Splitting {args.input} -> {args.output_dir}/")
        counts = split_dataset_to_components(Path(args.input), Path(args.output_dir))
        print(f"Created:")
        for name, count in counts.items():
            print(f"  {name}: {count}")

    elif args.command == 'build':
        print(f"Building from {args.prompts} + {args.outputs} -> {args.output}")
        count, stats = build_dataset_from_files(
            Path(args.prompts),
            Path(args.outputs),
            Path(args.output)
        )
        print(f"Built {count} examples")

    elif args.command == 'stats':
        print(f"Statistics for {args.input}")
        examples = []
        with open(args.input, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))

        stats = compute_stats(examples)
        print(f"\nTotal examples: {stats.total}")
        print(f"\nBy risk level:")
        for risk, count in sorted(stats.by_risk_level.items()):
            pct = (count / stats.total * 100) if stats.total > 0 else 0
            print(f"  {risk}: {count} ({pct:.1f}%)")
        print(f"\nTool calls:")
        print(f"  With: {stats.with_tool_calls}")
        print(f"  Without: {stats.without_tool_calls}")
        print(f"\nAverage lengths:")
        print(f"  Instruction: {stats.avg_instruction_length:.0f} chars")
        print(f"  Output: {stats.avg_output_length:.0f} chars")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
