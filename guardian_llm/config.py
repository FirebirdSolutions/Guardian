"""
Guardian LLM Configuration

Defines model configurations, training hyperparameters, and deployment settings
for the Guardian crisis detection system.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json
from pathlib import Path


class ModelSize(Enum):
    """Supported model sizes for Guardian deployment."""
    TINY = "tiny"      # ~500M params - mobile/edge
    SMALL = "small"    # ~1B params - efficient deployment
    MEDIUM = "medium"  # ~3B params - balanced
    LARGE = "large"    # ~7B params - maximum accuracy


class BaseModelType(Enum):
    """Supported base model architectures."""
    QWEN2_5 = "qwen2.5"
    LLAMA3 = "llama3"
    MISTRAL = "mistral"
    PHI3 = "phi3"
    GEMMA2 = "gemma2"


@dataclass
class GuardianConfig:
    """Configuration for Guardian LLM model."""

    # Model selection
    model_size: ModelSize = ModelSize.LARGE
    base_model_type: BaseModelType = BaseModelType.QWEN2_5
    base_model_id: str = "Qwen/Qwen2.5-7B-Instruct"

    # Model architecture
    max_seq_length: int = 2048
    use_flash_attention: bool = True
    rope_scaling: Optional[Dict[str, Any]] = None

    # LoRA configuration
    lora_r: int = 64
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])

    # Quantization
    load_in_4bit: bool = True
    load_in_8bit: bool = False
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True

    # Guardian-specific settings
    crisis_categories: List[str] = field(default_factory=lambda: [
        "suicide_ideation", "self_harm", "domestic_violence",
        "child_abuse", "substance_abuse", "eating_disorder",
        "youth_specific", "psychotic_symptoms", "cultural_maori_distress",
        "false_positive"
    ])

    risk_levels: List[str] = field(default_factory=lambda: [
        "CRITICAL", "HIGH", "MEDIUM", "LOW"
    ])

    # System prompt template
    system_prompt: str = """You are Guardian, an AI safety system.

VERIFIED NZ CRISIS RESOURCES:
• 111 - Emergency services
• 1737 - Mental health crisis (Free 24/7 call or text)
• 0800 543 354 - Lifeline NZ (Free 24/7)
• 0800 456 450 - Family Violence Hotline (Free 24/7)
• 0800 733 843 - Women's Refuge (Free 24/7)

KNOWN FAKE NUMBERS:
• 0800 543 800 - FAKE
• 988 - US crisis line (not NZ)"""

    # Chat template
    chat_template: str = "qwen"  # qwen, llama, chatml

    @classmethod
    def from_model_size(cls, size: ModelSize) -> "GuardianConfig":
        """Create config based on model size."""
        configs = {
            ModelSize.TINY: {
                "base_model_id": "Qwen/Qwen2.5-0.5B-Instruct",
                "lora_r": 16,
                "lora_alpha": 16,
                "max_seq_length": 1024,
            },
            ModelSize.SMALL: {
                "base_model_id": "Qwen/Qwen2.5-1.5B-Instruct",
                "lora_r": 32,
                "lora_alpha": 32,
                "max_seq_length": 1536,
            },
            ModelSize.MEDIUM: {
                "base_model_id": "Qwen/Qwen2.5-3B-Instruct",
                "lora_r": 48,
                "lora_alpha": 32,
                "max_seq_length": 2048,
            },
            ModelSize.LARGE: {
                "base_model_id": "Qwen/Qwen2.5-7B-Instruct",
                "lora_r": 64,
                "lora_alpha": 32,
                "max_seq_length": 2048,
            },
        }
        return cls(model_size=size, **configs[size])

    @classmethod
    def from_json(cls, path: str) -> "GuardianConfig":
        """Load config from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)

        # Convert enums
        if "model_size" in data:
            data["model_size"] = ModelSize(data["model_size"])
        if "base_model_type" in data:
            data["base_model_type"] = BaseModelType(data["base_model_type"])

        return cls(**data)

    def to_json(self, path: str):
        """Save config to JSON file."""
        data = {
            "model_size": self.model_size.value,
            "base_model_type": self.base_model_type.value,
            "base_model_id": self.base_model_id,
            "max_seq_length": self.max_seq_length,
            "use_flash_attention": self.use_flash_attention,
            "lora_r": self.lora_r,
            "lora_alpha": self.lora_alpha,
            "lora_dropout": self.lora_dropout,
            "lora_target_modules": self.lora_target_modules,
            "load_in_4bit": self.load_in_4bit,
            "load_in_8bit": self.load_in_8bit,
            "crisis_categories": self.crisis_categories,
            "risk_levels": self.risk_levels,
            "system_prompt": self.system_prompt,
            "chat_template": self.chat_template,
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


@dataclass
class TrainingConfig:
    """Training configuration for Guardian LLM."""

    # Data
    training_file: str = "combined_training_data.jsonl"
    validation_split: float = 0.1
    max_samples: Optional[int] = None  # None = use all

    # Training hyperparameters
    num_epochs: int = 20
    batch_size: int = 24
    gradient_accumulation_steps: int = 1
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    warmup_steps: int = 10
    warmup_ratio: float = 0.03
    max_grad_norm: float = 1.0

    # Learning rate schedule
    lr_scheduler_type: str = "cosine"  # cosine, linear, constant

    # Optimizer
    optimizer: str = "adamw_torch"  # adamw_torch, adamw_8bit, paged_adamw_8bit

    # Precision
    bf16: bool = True
    fp16: bool = False
    tf32: bool = True

    # Checkpointing
    output_dir: str = "./guardian-output"
    save_strategy: str = "epoch"
    save_total_limit: int = 5
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_loss"
    greater_is_better: bool = False

    # Evaluation
    eval_strategy: str = "epoch"
    eval_steps: int = 50

    # Logging
    logging_steps: int = 1
    logging_dir: str = "./logs"
    report_to: List[str] = field(default_factory=lambda: ["tensorboard"])

    # Reproducibility
    seed: int = 42
    data_seed: int = 42

    # Advanced
    gradient_checkpointing: bool = False
    group_by_length: bool = True
    ddp_find_unused_parameters: bool = False
    dataloader_num_workers: int = 4
    dataloader_pin_memory: bool = True

    # Early stopping
    early_stopping_patience: int = 3
    early_stopping_threshold: float = 0.01

    # Guardian-specific training settings
    crisis_weight_multiplier: float = 2.0  # Weight CRITICAL examples more
    balance_risk_levels: bool = True
    augment_data: bool = False

    @classmethod
    def from_json(cls, path: str) -> "TrainingConfig":
        """Load config from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)

    def to_json(self, path: str):
        """Save config to JSON file."""
        data = {
            "training_file": self.training_file,
            "validation_split": self.validation_split,
            "num_epochs": self.num_epochs,
            "batch_size": self.batch_size,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "learning_rate": self.learning_rate,
            "weight_decay": self.weight_decay,
            "warmup_steps": self.warmup_steps,
            "lr_scheduler_type": self.lr_scheduler_type,
            "bf16": self.bf16,
            "output_dir": self.output_dir,
            "save_strategy": self.save_strategy,
            "save_total_limit": self.save_total_limit,
            "eval_strategy": self.eval_strategy,
            "logging_steps": self.logging_steps,
            "seed": self.seed,
            "crisis_weight_multiplier": self.crisis_weight_multiplier,
            "balance_risk_levels": self.balance_risk_levels,
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


@dataclass
class InferenceConfig:
    """Configuration for Guardian inference."""

    # Generation parameters
    max_new_tokens: int = 512
    temperature: float = 0.1  # Low for consistent crisis response
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    do_sample: bool = True

    # Streaming
    stream: bool = True
    stream_chunk_size: int = 1

    # Batching
    batch_size: int = 1

    # Performance
    use_cache: bool = True
    num_beams: int = 1  # Greedy for speed

    # Guardian-specific
    enforce_structured_output: bool = True
    validate_resources: bool = True
    max_response_time_ms: int = 5000  # Max 5s for crisis response


@dataclass
class ExportConfig:
    """Configuration for model export."""

    # GGUF export
    export_gguf: bool = True
    gguf_quantization: str = "q4_k_m"  # q4_k_m, q5_k_m, q8_0, f16

    # ONNX export
    export_onnx: bool = False
    onnx_opset: int = 14

    # SafeTensors
    export_safetensors: bool = True

    # Merge LoRA
    merge_lora: bool = True

    # Output
    export_dir: str = "./guardian-export"
