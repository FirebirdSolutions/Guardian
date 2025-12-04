#!/usr/bin/env python3
"""
Guardian LLM - Command Line Interface

Usage:
    python -m guardian_llm <command> [options]

Commands:
    train           Train the Guardian LLM model
    prepare         Prepare and normalize training data
    normalize       Normalize existing training data for consistent tool calling
    process         Process external datasets (Mendeley, SWMH)
    batch-submit    Submit batch job to Anthropic API
    batch-download  Download and process batch results
    generate        Generate training data variations
    stats           Show training data statistics
    help            Show this help message

Examples:
    python -m guardian_llm train --model-size small --epochs 10
    python -m guardian_llm prepare input.jsonl output.jsonl
    python -m guardian_llm process mendeley data.csv output.jsonl
    python -m guardian_llm stats "Fine Tuning/training-data-final.jsonl"
"""

import sys


def show_help():
    """Show help message."""
    print(__doc__)
    print("For command-specific help, run:")
    print("    python -m guardian_llm <command> --help")


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    # Remove the command from argv so submodules see correct args
    sys.argv = [f"guardian_llm.{command}"] + sys.argv[2:]

    if command in ("help", "-h", "--help"):
        show_help()
        sys.exit(0)

    elif command == "train":
        from guardian_llm.scripts.train import main as train_main
        train_main()

    elif command == "prepare":
        from guardian_llm.scripts.prepare_data import main as prepare_main
        sys.exit(prepare_main())

    elif command == "normalize":
        from guardian_llm.scripts.normalize import main as normalize_main
        normalize_main()

    elif command == "process":
        from guardian_llm.scripts.process_external import main as process_main
        process_main()

    elif command in ("batch-submit", "submit"):
        from guardian_llm.scripts.batch_submit import main as submit_main
        submit_main()

    elif command in ("batch-download", "download"):
        from guardian_llm.scripts.batch_download import main as download_main
        download_main()

    elif command == "generate":
        from guardian_llm.scripts.generate_variations import main as generate_main
        generate_main()

    elif command == "stats":
        from guardian_llm.data_utils import compute_stats
        from pathlib import Path
        import json

        if len(sys.argv) < 2:
            print("Usage: python -m guardian_llm stats <file.jsonl>")
            sys.exit(1)

        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

        # Load examples from file
        examples = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))

        stats = compute_stats(examples)
        print(f"\nDataset Statistics: {filepath}")
        print("=" * 50)
        print(f"Total examples: {stats.total}")
        print(f"With tool calls: {stats.with_tool_calls}")
        print(f"Without tool calls: {stats.without_tool_calls}")
        print(f"\nBy risk level:")
        for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = stats.by_risk_level.get(level, 0)
            pct = (count / stats.total * 100) if stats.total > 0 else 0
            print(f"  {level}: {count} ({pct:.1f}%)")

    else:
        print(f"Unknown command: {command}")
        print("\nRun 'python -m guardian_llm help' for available commands")
        sys.exit(1)


if __name__ == "__main__":
    main()
