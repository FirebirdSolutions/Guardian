"""
Guardian LLM Data Processing

Dataset loading, preprocessing, and augmentation for Guardian training.
Supports weighted sampling for crisis-critical examples.
"""

import json
import random
import re
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
import logging

from datasets import Dataset, DatasetDict

from .config import TrainingConfig, GuardianConfig
from .regions import Region, RegionManager

logger = logging.getLogger(__name__)


@dataclass
class TrainingExample:
    """A single training example."""
    instruction: str
    output: str
    input: str = ""
    risk_level: str = "MEDIUM"
    categories: List[str] = None
    region: str = "NZ"
    weight: float = 1.0

    def __post_init__(self):
        if self.categories is None:
            self.categories = []


class GuardianDataset:
    """Dataset handler for Guardian training data."""

    RISK_LEVEL_WEIGHTS = {
        "CRITICAL": 2.0,  # Most important - oversample
        "HIGH": 1.5,
        "MEDIUM": 1.0,
        "LOW": 0.8,  # Slightly undersample to focus on crises
    }

    def __init__(
        self,
        config: TrainingConfig,
        model_config: Optional[GuardianConfig] = None,
    ):
        """Initialize dataset handler.

        Args:
            config: Training configuration
            model_config: Model configuration for formatting
        """
        self.config = config
        self.model_config = model_config or GuardianConfig()
        self.region_manager = RegionManager()
        self.examples: List[TrainingExample] = []

    def load_jsonl(self, file_path: str) -> List[TrainingExample]:
        """Load training data from JSONL file.

        Args:
            file_path: Path to JSONL file

        Returns:
            List of training examples
        """
        logger.info(f"Loading training data from {file_path}")
        examples = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    example = self._parse_example(data)
                    examples.append(example)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse line {line_num}: {e}")
                except Exception as e:
                    logger.warning(f"Error processing line {line_num}: {e}")

        logger.info(f"Loaded {len(examples)} examples")
        self.examples = examples
        return examples

    def _parse_example(self, data: Dict[str, Any]) -> TrainingExample:
        """Parse a single example from raw data.

        Args:
            data: Raw example data

        Returns:
            Parsed TrainingExample
        """
        instruction = data.get("instruction", "")
        output = data.get("output", "")
        input_text = data.get("input", "")

        # Extract risk level from output
        risk_level = self._extract_risk_level(output)

        # Extract categories from output
        categories = self._extract_categories(output)

        # Determine weight based on risk level
        weight = self.RISK_LEVEL_WEIGHTS.get(risk_level, 1.0)
        if self.config.crisis_weight_multiplier != 1.0:
            if risk_level in ["CRITICAL", "HIGH"]:
                weight *= self.config.crisis_weight_multiplier

        return TrainingExample(
            instruction=instruction,
            output=output,
            input=input_text,
            risk_level=risk_level,
            categories=categories,
            weight=weight,
        )

    def _extract_risk_level(self, output: str) -> str:
        """Extract risk level from output text.

        Args:
            output: Model output text

        Returns:
            Risk level string
        """
        # Look for RISK LEVEL: pattern
        match = re.search(r'RISK LEVEL:\s*(\w+)', output, re.IGNORECASE)
        if match:
            level = match.group(1).upper()
            if level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                return level

        # Fallback: check for keywords
        output_upper = output.upper()
        if "CRITICAL" in output_upper:
            return "CRITICAL"
        elif "HIGH" in output_upper:
            return "HIGH"
        elif "MEDIUM" in output_upper:
            return "MEDIUM"

        return "LOW"

    def _extract_categories(self, output: str) -> List[str]:
        """Extract crisis categories from output.

        Args:
            output: Model output text

        Returns:
            List of category strings
        """
        categories = []

        # Pattern matching for common categories
        category_patterns = {
            "suicide_ideation": r'suicid|death wish|end.*life|kill.*self',
            "self_harm": r'self.?harm|cut.*self|hurt.*self',
            "domestic_violence": r'domestic|dv|abuse|hit.*me|violence.*partner',
            "substance_abuse": r'drug|alcohol|substance|overdose|relapse',
            "psychotic_symptoms": r'psycho|voices|hallucin|delusion',
            "eating_disorder": r'eating|anorex|bulim|purge',
            "youth_specific": r'youth|teen|school|bully',
        }

        output_lower = output.lower()
        for category, pattern in category_patterns.items():
            if re.search(pattern, output_lower):
                categories.append(category)

        return categories

    def format_for_training(
        self,
        examples: Optional[List[TrainingExample]] = None,
    ) -> Dataset:
        """Format examples for training with chat template.

        Args:
            examples: Examples to format (uses self.examples if None)

        Returns:
            HuggingFace Dataset ready for training
        """
        if examples is None:
            examples = self.examples

        formatted_data = []
        for example in examples:
            text = self._format_example_text(example)
            formatted_data.append({
                "text": text,
                "risk_level": example.risk_level,
                "weight": example.weight,
            })

        return Dataset.from_list(formatted_data)

    def _format_example_text(self, example: TrainingExample) -> str:
        """Format a single example as training text.

        Args:
            example: Training example

        Returns:
            Formatted text string
        """
        instruction = example.instruction
        output = example.output

        # Use Qwen chat format (default)
        if self.model_config.chat_template == "qwen":
            text = f"<|im_start|>system\nYou are Guardian, an AI safety system.<|im_end|>\n"
            text += f"<|im_start|>user\n{instruction}<|im_end|>\n"
            text += f"<|im_start|>assistant\n{output}<|im_end|>"
        elif self.model_config.chat_template == "llama":
            text = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            text += f"You are Guardian, an AI safety system.<|eot_id|>"
            text += f"<|start_header_id|>user<|end_header_id|>\n\n{instruction}<|eot_id|>"
            text += f"<|start_header_id|>assistant<|end_header_id|>\n\n{output}<|eot_id|>"
        else:  # chatml
            text = f"<|system|>\nYou are Guardian, an AI safety system.</s>\n"
            text += f"<|user|>\n{instruction}</s>\n"
            text += f"<|assistant|>\n{output}</s>"

        return text

    def split_dataset(
        self,
        dataset: Dataset,
        validation_split: float = 0.1,
        seed: int = 42,
        stratify_by_risk: bool = True,
    ) -> DatasetDict:
        """Split dataset into train and validation sets.

        Args:
            dataset: Dataset to split
            validation_split: Fraction for validation
            seed: Random seed
            stratify_by_risk: Whether to stratify by risk level

        Returns:
            DatasetDict with 'train' and 'validation' splits
        """
        if stratify_by_risk and "risk_level" in dataset.column_names:
            # Stratified split by risk level
            train_examples = []
            val_examples = []

            # Group by risk level
            risk_groups = {}
            for idx, example in enumerate(dataset):
                risk = example.get("risk_level", "MEDIUM")
                if risk not in risk_groups:
                    risk_groups[risk] = []
                risk_groups[risk].append(idx)

            # Split each group
            random.seed(seed)
            for risk, indices in risk_groups.items():
                random.shuffle(indices)
                split_point = int(len(indices) * (1 - validation_split))
                train_examples.extend(indices[:split_point])
                val_examples.extend(indices[split_point:])

            # Create splits
            train_dataset = dataset.select(train_examples)
            val_dataset = dataset.select(val_examples)
        else:
            # Simple random split
            split = dataset.train_test_split(
                test_size=validation_split,
                seed=seed,
            )
            train_dataset = split["train"]
            val_dataset = split["test"]

        logger.info(f"Train size: {len(train_dataset)}, Validation size: {len(val_dataset)}")

        return DatasetDict({
            "train": train_dataset,
            "validation": val_dataset,
        })

    def get_risk_level_distribution(self) -> Dict[str, int]:
        """Get distribution of risk levels in dataset.

        Returns:
            Dict mapping risk level to count
        """
        distribution = {}
        for example in self.examples:
            level = example.risk_level
            distribution[level] = distribution.get(level, 0) + 1
        return distribution

    def balance_dataset(
        self,
        target_distribution: Optional[Dict[str, float]] = None,
    ) -> List[TrainingExample]:
        """Balance dataset by risk level through oversampling.

        Args:
            target_distribution: Target distribution (defaults to equal)

        Returns:
            Balanced list of examples
        """
        if not self.examples:
            return []

        # Group by risk level
        risk_groups = {}
        for example in self.examples:
            risk = example.risk_level
            if risk not in risk_groups:
                risk_groups[risk] = []
            risk_groups[risk].append(example)

        if target_distribution is None:
            # Default: match the largest group
            max_count = max(len(g) for g in risk_groups.values())
            target_distribution = {
                risk: max_count for risk in risk_groups.keys()
            }

        # Oversample to match target
        balanced = []
        for risk, examples in risk_groups.items():
            target = int(target_distribution.get(risk, len(examples)))
            if len(examples) >= target:
                balanced.extend(examples[:target])
            else:
                # Oversample
                balanced.extend(examples)
                remaining = target - len(examples)
                balanced.extend(random.choices(examples, k=remaining))

        random.shuffle(balanced)
        logger.info(f"Balanced dataset: {len(self.examples)} -> {len(balanced)} examples")

        return balanced

    def augment_example(
        self,
        example: TrainingExample,
        region: Region = Region.NZ,
    ) -> List[TrainingExample]:
        """Generate augmented variations of an example.

        Args:
            example: Original example
            region: Region for resource variations

        Returns:
            List of augmented examples (including original)
        """
        augmented = [example]

        # Simple augmentations for crisis detection
        instruction = example.instruction

        # Extract user message
        user_msg_match = re.search(r"User:\s*['\"](.+?)['\"]", instruction)
        if not user_msg_match:
            return augmented

        user_message = user_msg_match.group(1)

        # Augmentation 1: Lowercase
        if user_message != user_message.lower():
            new_instruction = instruction.replace(user_message, user_message.lower())
            augmented.append(TrainingExample(
                instruction=new_instruction,
                output=example.output,
                risk_level=example.risk_level,
                categories=example.categories,
                weight=example.weight,
            ))

        # Augmentation 2: Remove punctuation
        no_punct = re.sub(r'[.,!?;:]', '', user_message)
        if no_punct != user_message:
            new_instruction = instruction.replace(user_message, no_punct)
            augmented.append(TrainingExample(
                instruction=new_instruction,
                output=example.output,
                risk_level=example.risk_level,
                categories=example.categories,
                weight=example.weight * 0.9,  # Slightly lower weight for augmented
            ))

        return augmented

    def create_multi_region_dataset(
        self,
        regions: List[Region] = None,
    ) -> List[TrainingExample]:
        """Create dataset with examples for multiple regions.

        Args:
            regions: Regions to include (defaults to all)

        Returns:
            List of examples across regions
        """
        if regions is None:
            regions = [Region.NZ, Region.AU, Region.US, Region.UK]

        multi_region_examples = []

        for example in self.examples:
            # Original example (NZ)
            multi_region_examples.append(example)

            # Skip low-risk examples for other regions (reduce size)
            if example.risk_level == "LOW":
                continue

            # Create variations for other regions
            for region in regions:
                if region == Region.NZ:
                    continue

                # Update system prompt for region
                regional_prompt = self.region_manager.get_system_prompt(region)
                new_instruction = re.sub(
                    r'VERIFIED NZ CRISIS RESOURCES:.*?(?=Observation:)',
                    regional_prompt.split("Observation:")[0] if "Observation:" in regional_prompt else regional_prompt + "\n\n",
                    example.instruction,
                    flags=re.DOTALL,
                )

                # Update output resources (basic replacement)
                new_output = self._adapt_output_for_region(example.output, region)

                multi_region_examples.append(TrainingExample(
                    instruction=new_instruction,
                    output=new_output,
                    risk_level=example.risk_level,
                    categories=example.categories,
                    region=region.value,
                    weight=example.weight * 0.8,  # Slightly lower for regional variations
                ))

        logger.info(f"Created multi-region dataset: {len(multi_region_examples)} examples")
        return multi_region_examples

    def _adapt_output_for_region(self, output: str, region: Region) -> str:
        """Adapt output text for a different region.

        Args:
            output: Original output
            region: Target region

        Returns:
            Adapted output text
        """
        config = self.region_manager.get_config(region)

        # Replace NZ-specific numbers
        replacements = {
            "111": config.emergency_number,
            "1737": config.crisis_resources.get("mental_health", config.crisis_resources.get("lifeline")).number if "mental_health" in config.crisis_resources or "lifeline" in config.crisis_resources else "988",
            "0800 543 354": config.crisis_resources.get("lifeline").number if "lifeline" in config.crisis_resources else "",
        }

        new_output = output
        for old, new in replacements.items():
            if new:
                new_output = new_output.replace(old, new)

        # Update region references
        new_output = new_output.replace("region='NZ'", f"region='{region.value}'")
        new_output = new_output.replace("NZ crisis", f"{config.country_name} crisis")

        return new_output


def load_and_prepare_dataset(
    training_file: str,
    config: TrainingConfig,
    model_config: Optional[GuardianConfig] = None,
    tokenizer=None,
) -> Tuple[Dataset, Dataset]:
    """Convenience function to load and prepare dataset for training.

    Args:
        training_file: Path to training data file
        config: Training configuration
        model_config: Model configuration
        tokenizer: Tokenizer for tokenization

    Returns:
        Tuple of (train_dataset, eval_dataset)
    """
    dataset_handler = GuardianDataset(config, model_config)
    dataset_handler.load_jsonl(training_file)

    # Balance if configured
    if config.balance_risk_levels:
        balanced_examples = dataset_handler.balance_dataset()
    else:
        balanced_examples = dataset_handler.examples

    # Format for training
    formatted_dataset = dataset_handler.format_for_training(balanced_examples)

    # Tokenize if tokenizer provided
    if tokenizer is not None:
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=model_config.max_seq_length if model_config else 2048,
                padding="max_length",
            )

        formatted_dataset = formatted_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"],
        )

    # Split
    splits = dataset_handler.split_dataset(
        formatted_dataset,
        validation_split=config.validation_split,
        seed=config.seed,
    )

    return splits["train"], splits["validation"]
