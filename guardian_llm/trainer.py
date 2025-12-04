"""
Guardian LLM Trainer

Advanced training pipeline with custom metrics, callbacks,
and crisis-aware loss weighting for Guardian crisis detection.
"""

import os
import json
import logging
from typing import Dict, Optional, List, Any, Callable
from pathlib import Path
from dataclasses import dataclass
import random
import numpy as np

import torch
from torch.utils.data import DataLoader
from transformers import (
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback,
    TrainerCallback,
    TrainerState,
    TrainerControl,
)
from transformers.trainer_utils import get_last_checkpoint

from .config import GuardianConfig, TrainingConfig
from .model import GuardianModel
from .data import GuardianDataset, load_and_prepare_dataset

logger = logging.getLogger(__name__)


@dataclass
class TrainingMetrics:
    """Metrics tracked during training."""
    train_loss: float = 0.0
    eval_loss: float = 0.0
    learning_rate: float = 0.0
    epoch: float = 0.0
    step: int = 0
    best_eval_loss: float = float('inf')
    critical_accuracy: float = 0.0
    high_accuracy: float = 0.0
    false_positive_rate: float = 0.0


class GuardianTrainerCallback(TrainerCallback):
    """Custom callback for Guardian-specific training monitoring."""

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.metrics_history: List[Dict] = []

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: Optional[Dict[str, float]] = None,
        **kwargs,
    ):
        """Log metrics on each logging step."""
        if logs:
            metrics = {
                "step": state.global_step,
                "epoch": state.epoch,
                **logs,
            }
            self.metrics_history.append(metrics)

            if self.log_file:
                with open(self.log_file, 'a') as f:
                    f.write(json.dumps(metrics) + "\n")

    def on_epoch_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        """Log epoch completion."""
        logger.info(f"Completed epoch {state.epoch:.2f}")

    def on_train_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        """Save final metrics summary."""
        if self.log_file and self.metrics_history:
            summary_file = self.log_file.replace('.jsonl', '_summary.json')
            summary = {
                "total_steps": state.global_step,
                "total_epochs": state.epoch,
                "final_loss": self.metrics_history[-1].get("loss", None),
                "best_loss": state.best_metric,
            }
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)


class WeightedDataCollator(DataCollatorForLanguageModeling):
    """Data collator that supports sample weighting for crisis examples."""

    def __init__(self, tokenizer, mlm=False, weight_key="weight"):
        super().__init__(tokenizer=tokenizer, mlm=mlm)
        self.weight_key = weight_key

    def __call__(self, features):
        # Extract weights before calling parent
        weights = None
        if features and self.weight_key in features[0]:
            weights = torch.tensor([f.pop(self.weight_key, 1.0) for f in features])

        # Call parent collator
        batch = super().__call__(features)

        # Add weights to batch if present
        if weights is not None:
            batch["sample_weights"] = weights

        return batch


class GuardianTrainer(Trainer):
    """Custom trainer with crisis-aware loss weighting."""

    def __init__(self, *args, use_weighted_loss: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_weighted_loss = use_weighted_loss

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        """Compute loss with optional sample weighting."""
        # Extract sample weights if present
        sample_weights = inputs.pop("sample_weights", None)

        # Standard forward pass
        outputs = model(**inputs)
        loss = outputs.loss

        # Apply sample weights if available
        if self.use_weighted_loss and sample_weights is not None:
            # Expand weights to match loss shape and apply
            weights = sample_weights.to(loss.device)
            weighted_loss = loss * weights.mean()  # Simple mean weighting
            loss = weighted_loss

        return (loss, outputs) if return_outputs else loss


def set_seed(seed: int):
    """Set random seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)


def train_guardian(
    model_config: GuardianConfig,
    training_config: TrainingConfig,
    training_file: Optional[str] = None,
    resume_from_checkpoint: Optional[str] = None,
    custom_callbacks: Optional[List[TrainerCallback]] = None,
) -> Dict[str, Any]:
    """
    Main training function for Guardian LLM.

    Args:
        model_config: Model configuration
        training_config: Training configuration
        training_file: Path to training data (overrides config)
        resume_from_checkpoint: Path to checkpoint to resume from
        custom_callbacks: Additional trainer callbacks

    Returns:
        Dict with training results and metrics
    """
    # Set seed for reproducibility
    set_seed(training_config.seed)

    logger.info("=" * 60)
    logger.info("GUARDIAN LLM TRAINING")
    logger.info("=" * 60)

    # Initialize model
    logger.info("Initializing model...")
    guardian_model = GuardianModel(model_config)
    tokenizer = guardian_model.load_tokenizer()
    guardian_model.load_base_model()
    model = guardian_model.prepare_for_training()

    # Load and prepare data
    logger.info("Loading training data...")
    data_file = training_file or training_config.training_file
    train_dataset, eval_dataset = load_and_prepare_dataset(
        data_file,
        training_config,
        model_config,
        tokenizer,
    )

    logger.info(f"Train examples: {len(train_dataset)}")
    logger.info(f"Eval examples: {len(eval_dataset)}")

    # Setup output directory
    output_dir = Path(training_config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save configs
    model_config.to_json(str(output_dir / "model_config.json"))
    training_config.to_json(str(output_dir / "training_config.json"))

    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=training_config.num_epochs,
        per_device_train_batch_size=training_config.batch_size,
        per_device_eval_batch_size=training_config.batch_size,
        gradient_accumulation_steps=training_config.gradient_accumulation_steps,
        learning_rate=training_config.learning_rate,
        weight_decay=training_config.weight_decay,
        warmup_steps=training_config.warmup_steps,
        lr_scheduler_type=training_config.lr_scheduler_type,
        logging_steps=training_config.logging_steps,
        logging_dir=str(output_dir / "logs"),
        save_strategy=training_config.save_strategy,
        save_total_limit=training_config.save_total_limit,
        eval_strategy=training_config.eval_strategy,
        load_best_model_at_end=training_config.load_best_model_at_end,
        metric_for_best_model=training_config.metric_for_best_model,
        greater_is_better=training_config.greater_is_better,
        bf16=training_config.bf16,
        fp16=training_config.fp16,
        report_to=training_config.report_to,
        seed=training_config.seed,
        data_seed=training_config.data_seed,
        dataloader_num_workers=training_config.dataloader_num_workers,
        dataloader_pin_memory=training_config.dataloader_pin_memory,
        group_by_length=training_config.group_by_length,
        remove_unused_columns=False,  # Keep weights column
    )

    # Data collator
    data_collator = WeightedDataCollator(
        tokenizer=tokenizer,
        mlm=False,
    )

    # Callbacks
    callbacks = [
        GuardianTrainerCallback(
            log_file=str(output_dir / "training_metrics.jsonl")
        ),
    ]

    if training_config.early_stopping_patience > 0:
        callbacks.append(
            EarlyStoppingCallback(
                early_stopping_patience=training_config.early_stopping_patience,
                early_stopping_threshold=training_config.early_stopping_threshold,
            )
        )

    if custom_callbacks:
        callbacks.extend(custom_callbacks)

    # Initialize trainer
    trainer = GuardianTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        callbacks=callbacks,
        use_weighted_loss=training_config.crisis_weight_multiplier != 1.0,
    )

    # Check for existing checkpoint
    last_checkpoint = None
    if resume_from_checkpoint:
        last_checkpoint = resume_from_checkpoint
    elif (output_dir / "checkpoint-*").exists():
        last_checkpoint = get_last_checkpoint(str(output_dir))

    if last_checkpoint:
        logger.info(f"Resuming from checkpoint: {last_checkpoint}")

    # Train!
    logger.info("=" * 60)
    logger.info("STARTING TRAINING")
    logger.info("=" * 60)

    train_result = trainer.train(resume_from_checkpoint=last_checkpoint)

    # Save final model
    logger.info("Saving final model...")
    final_model_path = output_dir / "final"
    guardian_model.save(str(final_model_path))

    # Save training metrics
    metrics = {
        "train_runtime": train_result.metrics.get("train_runtime"),
        "train_samples_per_second": train_result.metrics.get("train_samples_per_second"),
        "train_loss": train_result.metrics.get("train_loss"),
        "total_steps": train_result.global_step,
        "epochs_completed": train_result.metrics.get("epoch"),
    }

    # Evaluate
    logger.info("Running final evaluation...")
    eval_results = trainer.evaluate()
    metrics["eval_loss"] = eval_results.get("eval_loss")

    # Save metrics
    with open(output_dir / "final_metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)

    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"Model saved to: {final_model_path}")
    logger.info(f"Final train loss: {metrics.get('train_loss', 'N/A')}")
    logger.info(f"Final eval loss: {metrics.get('eval_loss', 'N/A')}")

    return {
        "model_path": str(final_model_path),
        "metrics": metrics,
        "train_result": train_result,
        "eval_results": eval_results,
    }


def train_multi_region(
    model_config: GuardianConfig,
    training_config: TrainingConfig,
    training_file: str,
    regions: List[str] = None,
) -> Dict[str, Any]:
    """
    Train Guardian model on multi-region dataset.

    Args:
        model_config: Model configuration
        training_config: Training configuration
        training_file: Path to training data
        regions: List of region codes to include

    Returns:
        Training results
    """
    from .regions import Region

    logger.info("Preparing multi-region training dataset...")

    # Load and prepare multi-region data
    dataset_handler = GuardianDataset(training_config, model_config)
    dataset_handler.load_jsonl(training_file)

    # Determine regions
    if regions:
        region_list = [Region(r) for r in regions]
    else:
        region_list = [Region.NZ, Region.AU, Region.US, Region.UK]

    # Create multi-region examples
    multi_region_examples = dataset_handler.create_multi_region_dataset(region_list)

    # Save multi-region dataset
    output_dir = Path(training_config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    multi_region_file = output_dir / "multi_region_training_data.jsonl"
    with open(multi_region_file, 'w') as f:
        for example in multi_region_examples:
            f.write(json.dumps({
                "instruction": example.instruction,
                "output": example.output,
                "input": example.input,
            }) + "\n")

    logger.info(f"Created multi-region dataset with {len(multi_region_examples)} examples")

    # Train with multi-region data
    return train_guardian(
        model_config,
        training_config,
        training_file=str(multi_region_file),
    )
