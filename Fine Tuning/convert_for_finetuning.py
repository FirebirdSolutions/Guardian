#!/usr/bin/env python3
"""
Convert training data to various fine-tuning formats.
Handles Alpaca, ChatML, and other common formats.
"""

import json
import sys
from pathlib import Path


def to_alpaca_format(record):
    """Convert to Alpaca/Instruction format."""
    return {
        "instruction": record["prompt"],
        "input": "",  # Usually empty for instruction tuning
        "output": record["response"]
    }


def to_chatml_format(record):
    """Convert to ChatML conversational format."""
    return {
        "messages": [
            {"role": "user", "content": record["prompt"]},
            {"role": "assistant", "content": record["response"]}
        ]
    }


def to_openai_format(record):
    """Convert to OpenAI fine-tuning format."""
    return {
        "messages": [
            {"role": "system", "content": "You are Echo, a helpful Kiwi AI assistant. You're direct, occasionally sweary about tech problems, and actually useful."},
            {"role": "user", "content": record["prompt"]},
            {"role": "assistant", "content": record["response"]}
        ]
    }


def to_llama_format(record):
    """Convert to Llama prompt format (text only)."""
    return {
        "text": f"<s>[INST] {record['prompt']} [/INST] {record['response']} </s>"
    }


def to_mistral_format(record):
    """Convert to Mistral prompt format."""
    return {
        "text": f"[INST] {record['prompt']} [/INST]{record['response']}</s>"
    }


def convert_dataset(input_path, output_path, format_type="alpaca"):
    """
    Convert dataset to specified format.
    
    Args:
        input_path: Input JSONL file
        output_path: Output JSONL file
        format_type: alpaca, chatml, openai, llama, mistral
    """
    converters = {
        "alpaca": to_alpaca_format,
        "chatml": to_chatml_format,
        "openai": to_openai_format,
        "llama": to_llama_format,
        "mistral": to_mistral_format
    }
    
    if format_type not in converters:
        print(f"Error: Unknown format '{format_type}'")
        print(f"Available formats: {', '.join(converters.keys())}")
        sys.exit(1)
    
    converter = converters[format_type]
    
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    converted = 0
    skipped = 0
    
    with open(input_file, 'r', encoding='utf-8') as inf, \
         open(output_path, 'w', encoding='utf-8') as outf:
        
        for line_num, line in enumerate(inf, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                record = json.loads(line)
                
                # Validate required fields
                if "prompt" not in record or "response" not in record:
                    print(f"Warning: Skipping line {line_num} - missing prompt or response")
                    skipped += 1
                    continue
                
                # Skip empty prompts/responses
                if not record["prompt"].strip() or not record["response"].strip():
                    skipped += 1
                    continue
                
                converted_record = converter(record)
                outf.write(json.dumps(converted_record, ensure_ascii=False) + '\n')
                converted += 1
                
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping line {line_num} - invalid JSON: {e}")
                skipped += 1
                continue
            except Exception as e:
                print(f"Warning: Skipping line {line_num} - error: {e}")
                skipped += 1
                continue
    
    print(f"\n✅ Conversion complete!")
    print(f"   Format: {format_type}")
    print(f"   Converted: {converted} records")
    print(f"   Skipped: {skipped} records")
    print(f"   Output: {output_path}")
    
    # Show sample
    print(f"\n📄 Sample output (first record):")
    with open(output_path, 'r', encoding='utf-8') as f:
        first = json.loads(f.readline())
        print(json.dumps(first, indent=2, ensure_ascii=False)[:500] + "...")


def main():
    if len(sys.argv) < 3:
        print("""
Dataset Format Converter for Fine-Tuning

Usage:
  python convert_for_finetuning.py <input.jsonl> <output.jsonl> [format]

Formats:
  alpaca    - Alpaca/Instruction format (default)
              {"instruction": "...", "input": "", "output": "..."}
  
  chatml    - ChatML conversational format
              {"messages": [{"role": "user", "content": "..."}, ...]}
  
  openai    - OpenAI fine-tuning format (includes system message)
              {"messages": [{"role": "system", ...}, {"role": "user", ...}, ...]}
  
  llama     - Llama prompt template format
              {"text": "<s>[INST] ... [/INST] ... </s>"}
  
  mistral   - Mistral prompt template format
              {"text": "[INST] ... [/INST]...</s>"}

Examples:
  # Convert to Alpaca format
  python convert_for_finetuning.py final_training.jsonl alpaca_format.jsonl alpaca
  
  # Convert to ChatML format
  python convert_for_finetuning.py final_training.jsonl chatml_format.jsonl chatml
  
  # Convert to Llama format
  python convert_for_finetuning.py final_training.jsonl llama_format.jsonl llama

Notes:
  - Input must be JSONL with "prompt" and "response" fields
  - Output is JSONL in the specified format
  - Empty or invalid records are skipped
        """)
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    format_type = sys.argv[3] if len(sys.argv) > 3 else "alpaca"
    
    print(f"Converting {input_path} to {format_type} format...")
    convert_dataset(input_path, output_path, format_type)


if __name__ == "__main__":
    main()
