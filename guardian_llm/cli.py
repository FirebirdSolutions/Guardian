#!/usr/bin/env python3
"""
Guardian LLM Command Line Interface

Run inference on trained Guardian models from the command line.

Usage:
    python -m guardian_llm.cli [OPTIONS] MESSAGE

Examples:
    # Basic usage
    python -m guardian_llm.cli "I'm feeling hopeless"

    # Specify model and region
    python -m guardian_llm.cli --model ./guardian-output/final --region AU "I need help"

    # Interactive mode
    python -m guardian_llm.cli --interactive
"""

import argparse
import sys
import json
from pathlib import Path

from .inference import GuardianInference, GuardianPipeline, create_inference_engine
from .regions import Region
from .config import InferenceConfig


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Guardian LLM - Crisis Detection Inference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "message",
        nargs="?",
        default=None,
        help="Message to analyze (or use --interactive)",
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        default="./guardian-output/final",
        help="Path to trained model",
    )

    parser.add_argument(
        "--region", "-r",
        type=str,
        default="NZ",
        choices=["NZ", "AU", "US", "UK", "CA", "IE"],
        help="Region for crisis resources (default: NZ)",
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode",
    )

    parser.add_argument(
        "--stream", "-s",
        action="store_true",
        help="Stream output tokens",
    )

    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON",
    )

    parser.add_argument(
        "--no-tools",
        action="store_true",
        help="Don't execute tool calls",
    )

    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.1,
        help="Generation temperature (default: 0.1)",
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=512,
        help="Maximum tokens to generate (default: 512)",
    )

    parser.add_argument(
        "--resources-only",
        action="store_true",
        help="Only show crisis resources for region",
    )

    return parser.parse_args()


def print_response(response, as_json: bool = False):
    """Print response in human-readable or JSON format."""
    if as_json:
        output = {
            "risk_level": response.risk_level,
            "patterns_detected": response.patterns_detected,
            "escalation_required": response.escalation_required,
            "crisis_resources": response.crisis_resources,
            "output": response.output,
            "inference_time_ms": response.inference_time_ms,
        }
        print(json.dumps(output, indent=2))
    else:
        # Color coding for risk levels
        colors = {
            "CRITICAL": "\033[91m",  # Red
            "HIGH": "\033[93m",       # Yellow
            "MEDIUM": "\033[94m",     # Blue
            "LOW": "\033[92m",        # Green
        }
        reset = "\033[0m"

        color = colors.get(response.risk_level, "")

        print("\n" + "=" * 50)
        print(f"{color}RISK LEVEL: {response.risk_level}{reset}")
        print("=" * 50)

        if response.patterns_detected:
            print(f"\nPatterns Detected: {', '.join(response.patterns_detected)}")

        if response.escalation_required:
            print(f"\n{colors['CRITICAL']}⚠️  ESCALATION REQUIRED{reset}")

        if response.intervention_message:
            print(f"\n{response.intervention_message}")

        if response.crisis_resources:
            print("\nCrisis Resources:")
            for resource in response.crisis_resources[:5]:
                print(f"  • {resource['number']} - {resource['name']}")
                if resource.get('availability'):
                    print(f"    ({resource['availability']}, {resource.get('cost', 'Free')})")

        print(f"\n[{response.inference_time_ms:.0f}ms | {response.tokens_generated} tokens]")


def interactive_mode(engine: GuardianInference, region: str, stream: bool):
    """Run interactive session."""
    print("\n" + "=" * 50)
    print("Guardian LLM - Interactive Mode")
    print("=" * 50)
    print(f"Region: {region}")
    print("Type 'quit' or 'exit' to end session")
    print("Type 'region <code>' to change region")
    print("=" * 50 + "\n")

    current_region = region

    while True:
        try:
            message = input("\nYou: ").strip()

            if not message:
                continue

            if message.lower() in ["quit", "exit", "q"]:
                print("Goodbye. Take care.")
                break

            if message.lower().startswith("region "):
                new_region = message.split()[1].upper()
                try:
                    Region(new_region)
                    current_region = new_region
                    print(f"Region changed to: {current_region}")
                    continue
                except ValueError:
                    print(f"Unknown region: {new_region}")
                    print("Valid regions: NZ, AU, US, UK, CA, IE")
                    continue

            # Generate response
            if stream:
                print("\nGuardian: ", end="", flush=True)
                for token in engine.generate(message, region=current_region, stream=True):
                    print(token, end="", flush=True)
                print()
            else:
                response = engine.generate(message, region=current_region)
                print_response(response)

        except KeyboardInterrupt:
            print("\n\nGoodbye. Take care.")
            break
        except EOFError:
            break


def main():
    """Main entry point."""
    args = parse_args()

    # Resources only mode - doesn't need model
    if args.resources_only:
        from .tools import GuardianTools
        tools = GuardianTools(Region(args.region))
        result = tools._get_crisis_resources(args.region, "mental_health")

        if args.json:
            print(json.dumps(result.data, indent=2))
        else:
            print(f"\nCrisis Resources for {args.region}:")
            print("-" * 40)
            for resource in result.data["resources"]:
                print(f"  {resource['number']} - {resource['name']}")
                print(f"    {resource['description']}")
                print(f"    {resource['availability']} | {resource['cost']}")
                print()
        return

    # Check model exists
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Error: Model not found at {args.model}")
        print("Train a model first with: python train_guardian_llm.py")
        sys.exit(1)

    # Create inference engine
    inference_config = InferenceConfig(
        temperature=args.temperature,
        max_new_tokens=args.max_tokens,
        stream=args.stream,
    )

    print(f"Loading model from {args.model}...")
    engine = create_inference_engine(
        args.model,
        region=args.region,
        **vars(inference_config),
    )

    # Interactive mode
    if args.interactive:
        interactive_mode(engine, args.region, args.stream)
        return

    # Single message mode
    if not args.message:
        print("Error: No message provided. Use --interactive or provide a message.")
        sys.exit(1)

    # Generate response
    response = engine.generate(
        args.message,
        region=args.region,
        execute_tools=not args.no_tools,
    )

    print_response(response, as_json=args.json)


if __name__ == "__main__":
    main()
