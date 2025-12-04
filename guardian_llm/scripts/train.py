#!/usr/bin/env python3
"""
Guardian LLM Training Script

Train a custom crisis detection LLM using the Guardian framework.

Usage:
    python -m guardian_llm.scripts.train [OPTIONS]

Examples:
    # Train with defaults (7B model)
    python -m guardian_llm.scripts.train

    # Train smaller model for faster iteration
    python -m guardian_llm.scripts.train --model-size small --epochs 10

    # Train with multi-region support
    python -m guardian_llm.scripts.train --multi-region --regions NZ,AU,US,UK

    # Resume from checkpoint
    python -m guardian_llm.scripts.train --resume ./guardian-output/checkpoint-500
"""

import argparse
import logging
import sys
from pathlib import Path

from guardian_llm.config import (
    GuardianConfig,
    TrainingConfig,
    ModelSize,
)
from guardian_llm.trainer import train_guardian, train_multi_region, set_seed
from guardian_llm.evaluator import CrisisEvaluator, quick_evaluate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Train Guardian LLM for crisis detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Model Sizes:
  tiny    - ~500M params, fastest training, mobile deployment
  small   - ~1B params, good balance of speed and quality
  medium  - ~3B params, better accuracy
  large   - ~7B params, best accuracy (default)

Training Tips:
  - Start with 'small' for quick experiments
  - Use 'large' for production models
  - Monitor critical_recall - must be near 100%
  - False positive rate should be < 20%
        """,
    )

    # Model configuration
    parser.add_argument(
        "--model-size",
        type=str,
        choices=["tiny", "small", "medium", "large"],
        default="large",
        help="Model size to train (default: large)",
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default=None,
        help="Override base model ID (e.g., Qwen/Qwen2.5-3B-Instruct)",
    )

    # Data
    parser.add_argument(
        "--training-file",
        type=str,
        default="Fine Tuning/training-data-final.jsonl",
        help="Path to training data JSONL file",
    )
    parser.add_argument(
        "--validation-split",
        type=float,
        default=0.1,
        help="Fraction of data for validation (default: 0.1)",
    )

    # Training hyperparameters
    parser.add_argument(
        "--epochs",
        type=int,
        default=20,
        help="Number of training epochs (default: 20)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=24,
        help="Training batch size (default: 24)",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=5e-5,
        help="Learning rate (default: 5e-5)",
    )
    parser.add_argument(
        "--warmup-steps",
        type=int,
        default=10,
        help="Warmup steps (default: 10)",
    )

    # LoRA configuration
    parser.add_argument(
        "--lora-r",
        type=int,
        default=None,
        help="LoRA rank (default: based on model size)",
    )
    parser.add_argument(
        "--lora-alpha",
        type=int,
        default=32,
        help="LoRA alpha (default: 32)",
    )

    # Output
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./guardian-output",
        help="Output directory for model and logs",
    )
    parser.add_argument(
        "--save-total-limit",
        type=int,
        default=5,
        help="Maximum checkpoints to keep (default: 5)",
    )

    # Multi-region training
    parser.add_argument(
        "--multi-region",
        action="store_true",
        help="Train with multi-region support",
    )
    parser.add_argument(
        "--regions",
        type=str,
        default="NZ,AU,US,UK",
        help="Comma-separated list of regions (default: NZ,AU,US,UK)",
    )

    # Training options
    parser.add_argument(
        "--crisis-weight",
        type=float,
        default=2.0,
        help="Weight multiplier for CRITICAL/HIGH examples (default: 2.0)",
    )
    parser.add_argument(
        "--balance-dataset",
        action="store_true",
        help="Balance dataset by risk level",
    )
    parser.add_argument(
        "--early-stopping",
        type=int,
        default=3,
        help="Early stopping patience (0 to disable)",
    )

    # Resume/checkpoint
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Path to checkpoint to resume from",
    )

    # Evaluation
    parser.add_argument(
        "--eval-after-training",
        action="store_true",
        default=True,
        help="Run evaluation after training",
    )
    parser.add_argument(
        "--eval-samples",
        type=int,
        default=100,
        help="Number of samples for quick evaluation",
    )

    # Misc
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--bf16",
        action="store_true",
        default=True,
        help="Use bfloat16 precision",
    )
    parser.add_argument(
        "--no-bf16",
        action="store_true",
        help="Disable bfloat16 (use float16)",
    )

    return parser.parse_args()


def main():
    """Main training function."""
    args = parse_args()

    print("=" * 60)
    print("GUARDIAN LLM TRAINING")
    print("=" * 60)
    print(f"Model size: {args.model_size}")
    print(f"Training file: {args.training_file}")
    print(f"Output directory: {args.output_dir}")
    print(f"Multi-region: {args.multi_region}")
    print("=" * 60)

    # Set seed
    set_seed(args.seed)

    # Create model config based on size
    model_size = ModelSize(args.model_size)
    model_config = GuardianConfig.from_model_size(model_size)

    # Override base model if specified
    if args.base_model:
        model_config.base_model_id = args.base_model

    # Override LoRA settings if specified
    if args.lora_r:
        model_config.lora_r = args.lora_r
    model_config.lora_alpha = args.lora_alpha

    # Create training config
    training_config = TrainingConfig(
        training_file=args.training_file,
        validation_split=args.validation_split,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        warmup_steps=args.warmup_steps,
        output_dir=args.output_dir,
        save_total_limit=args.save_total_limit,
        seed=args.seed,
        bf16=args.bf16 and not args.no_bf16,
        fp16=args.no_bf16,
        crisis_weight_multiplier=args.crisis_weight,
        balance_risk_levels=args.balance_dataset,
        early_stopping_patience=args.early_stopping,
    )

    # Verify training file exists
    if not Path(args.training_file).exists():
        logger.error(f"Training file not found: {args.training_file}")
        sys.exit(1)

    # Train
    try:
        if args.multi_region:
            regions = args.regions.split(",")
            logger.info(f"Training with multi-region support: {regions}")
            results = train_multi_region(
                model_config,
                training_config,
                args.training_file,
                regions=regions,
            )
        else:
            results = train_guardian(
                model_config,
                training_config,
                training_file=args.training_file,
                resume_from_checkpoint=args.resume,
            )

        print("\n" + "=" * 60)
        print("TRAINING COMPLETE!")
        print("=" * 60)
        print(f"Model saved to: {results['model_path']}")
        print(f"Final train loss: {results['metrics'].get('train_loss', 'N/A')}")
        print(f"Final eval loss: {results['metrics'].get('eval_loss', 'N/A')}")

        # Run evaluation if requested
        if args.eval_after_training:
            print("\n" + "=" * 60)
            print("RUNNING EVALUATION")
            print("=" * 60)

            from guardian_llm.model import GuardianModel

            model = GuardianModel.from_pretrained(results['model_path'])
            eval_metrics = quick_evaluate(
                model.model,
                model.tokenizer,
                args.training_file,
                num_samples=args.eval_samples,
            )

            print("\nEvaluation Results:")
            print(f"  Risk Level Accuracy: {eval_metrics['risk_accuracy']:.2%}")
            print(f"  Critical Recall: {eval_metrics['critical_recall']:.2%}")
            print(f"  Critical FN Rate: {eval_metrics['critical_fn_rate']:.2%}")
            print(f"  Tool Call F1: {eval_metrics['tool_f1']:.2%}")
            print(f"  False Positive Rate: {eval_metrics['fp_rate']:.2%}")
            print(f"  Avg Latency: {eval_metrics['avg_latency_ms']:.1f}ms")

            if eval_metrics['critical_fn_rate'] > 0:
                print("\n  WARNING: Some critical cases were missed!")
                print("   Consider increasing training epochs or data quality.")

    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
