"""
Guardian LLM Model

Custom model loading, architecture configuration, and LoRA setup
for the Guardian crisis detection system.
"""

import torch
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import json
import logging

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    PreTrainedModel,
    PreTrainedTokenizer,
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    PeftModel,
    TaskType,
)

from .config import GuardianConfig

logger = logging.getLogger(__name__)


class GuardianModel:
    """Guardian LLM model wrapper with LoRA support."""

    def __init__(self, config: Optional[GuardianConfig] = None):
        """Initialize Guardian model.

        Args:
            config: Model configuration. If None, uses default config.
        """
        self.config = config or GuardianConfig()
        self.model: Optional[PreTrainedModel] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None
        self.is_loaded = False
        self.is_peft_model = False

    def load_tokenizer(self) -> PreTrainedTokenizer:
        """Load and configure the tokenizer."""
        logger.info(f"Loading tokenizer from {self.config.base_model_id}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model_id,
            trust_remote_code=True,
            padding_side="right",
        )

        # Ensure pad token is set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        logger.info("Tokenizer loaded successfully")
        return self.tokenizer

    def load_base_model(
        self,
        device_map: str = "auto",
        torch_dtype: Optional[torch.dtype] = None,
    ) -> PreTrainedModel:
        """Load the base model with quantization if configured.

        Args:
            device_map: Device mapping strategy
            torch_dtype: Torch dtype for model weights

        Returns:
            Loaded model
        """
        logger.info(f"Loading base model: {self.config.base_model_id}")

        # Configure quantization
        quantization_config = None
        if self.config.load_in_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=getattr(
                    torch, self.config.bnb_4bit_compute_dtype
                ),
                bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=self.config.bnb_4bit_use_double_quant,
            )
            logger.info("Using 4-bit quantization")
        elif self.config.load_in_8bit:
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)
            logger.info("Using 8-bit quantization")

        # Determine dtype
        if torch_dtype is None:
            torch_dtype = torch.float16

        # Model loading arguments
        model_kwargs = {
            "device_map": device_map,
            "trust_remote_code": True,
            "torch_dtype": torch_dtype,
        }

        if quantization_config:
            model_kwargs["quantization_config"] = quantization_config

        # Enable flash attention if available
        if self.config.use_flash_attention:
            try:
                model_kwargs["attn_implementation"] = "flash_attention_2"
                logger.info("Using Flash Attention 2")
            except Exception:
                logger.warning("Flash Attention not available, using default")

        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model_id,
            **model_kwargs,
        )

        self.is_loaded = True
        logger.info(f"Model loaded: {self.model.config.model_type}")
        return self.model

    def prepare_for_training(self) -> PreTrainedModel:
        """Prepare model for LoRA training.

        Returns:
            Model with LoRA adapters
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_base_model() first.")

        logger.info("Preparing model for LoRA training")

        # Prepare for k-bit training if quantized
        if self.config.load_in_4bit or self.config.load_in_8bit:
            self.model = prepare_model_for_kbit_training(
                self.model,
                use_gradient_checkpointing=True,
            )

        # Configure LoRA
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )

        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        self.is_peft_model = True

        # Print trainable parameters
        self._print_trainable_parameters()

        return self.model

    def _print_trainable_parameters(self):
        """Print number of trainable parameters."""
        trainable_params = 0
        all_params = 0
        for _, param in self.model.named_parameters():
            all_params += param.numel()
            if param.requires_grad:
                trainable_params += param.numel()

        trainable_pct = 100 * trainable_params / all_params
        logger.info(
            f"Trainable params: {trainable_params:,} || "
            f"All params: {all_params:,} || "
            f"Trainable%: {trainable_pct:.4f}%"
        )

    def load_adapter(self, adapter_path: str) -> PreTrainedModel:
        """Load a trained LoRA adapter.

        Args:
            adapter_path: Path to the adapter weights

        Returns:
            Model with adapter loaded
        """
        if not self.is_loaded:
            self.load_tokenizer()
            self.load_base_model()

        logger.info(f"Loading adapter from {adapter_path}")
        self.model = PeftModel.from_pretrained(
            self.model,
            adapter_path,
            is_trainable=False,
        )
        self.is_peft_model = True
        logger.info("Adapter loaded successfully")
        return self.model

    def merge_and_unload(self) -> PreTrainedModel:
        """Merge LoRA weights into base model and unload adapter.

        Returns:
            Merged model without adapters
        """
        if not self.is_peft_model:
            logger.warning("No adapter to merge")
            return self.model

        logger.info("Merging LoRA weights into base model")
        self.model = self.model.merge_and_unload()
        self.is_peft_model = False
        logger.info("Merge complete")
        return self.model

    def save(self, output_path: str, save_tokenizer: bool = True):
        """Save model and optionally tokenizer.

        Args:
            output_path: Directory to save to
            save_tokenizer: Whether to save tokenizer
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving model to {output_path}")

        if self.is_peft_model:
            self.model.save_pretrained(output_path)
        else:
            self.model.save_pretrained(output_path, safe_serialization=True)

        if save_tokenizer and self.tokenizer:
            self.tokenizer.save_pretrained(output_path)

        # Save config
        self.config.to_json(str(output_path / "guardian_config.json"))

        logger.info("Model saved successfully")

    @classmethod
    def from_pretrained(
        cls,
        model_path: str,
        config: Optional[GuardianConfig] = None,
        device_map: str = "auto",
    ) -> "GuardianModel":
        """Load a trained Guardian model.

        Args:
            model_path: Path to saved model
            config: Optional config override
            device_map: Device mapping

        Returns:
            Loaded GuardianModel instance
        """
        model_path = Path(model_path)

        # Try to load config from saved model
        config_path = model_path / "guardian_config.json"
        if config is None and config_path.exists():
            config = GuardianConfig.from_json(str(config_path))
        elif config is None:
            config = GuardianConfig()

        instance = cls(config)

        # Check if this is a LoRA adapter or full model
        adapter_config_path = model_path / "adapter_config.json"
        if adapter_config_path.exists():
            # This is a LoRA adapter
            instance.load_tokenizer()
            instance.load_base_model(device_map=device_map)
            instance.load_adapter(str(model_path))
        else:
            # This is a full/merged model
            instance.config.base_model_id = str(model_path)
            instance.load_tokenizer()
            instance.load_base_model(device_map=device_map)

        return instance

    def format_prompt(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        region: str = "NZ",
    ) -> str:
        """Format a message using the model's chat template.

        Args:
            user_message: User's input message
            system_prompt: Optional custom system prompt
            region: Region code for crisis resources

        Returns:
            Formatted prompt string
        """
        if system_prompt is None:
            system_prompt = self.config.system_prompt

        # Build instruction in Guardian format
        instruction = f"{system_prompt}\n\nObservation: User: '{user_message}'"

        # Use Qwen chat template
        if self.config.chat_template == "qwen":
            text = f"<|im_start|>system\nYou are Guardian, an AI safety system.<|im_end|>\n"
            text += f"<|im_start|>user\n{instruction}<|im_end|>\n"
            text += f"<|im_start|>assistant\n"
        elif self.config.chat_template == "llama":
            text = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            text += f"You are Guardian, an AI safety system.<|eot_id|>"
            text += f"<|start_header_id|>user<|end_header_id|>\n\n{instruction}<|eot_id|>"
            text += f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        else:  # chatml
            text = f"<|system|>\nYou are Guardian, an AI safety system.</s>\n"
            text += f"<|user|>\n{instruction}</s>\n"
            text += f"<|assistant|>\n"

        return text

    def get_device(self) -> torch.device:
        """Get the device the model is on."""
        if self.model is None:
            return torch.device("cpu")
        return next(self.model.parameters()).device

    def to(self, device: torch.device) -> "GuardianModel":
        """Move model to device."""
        if self.model:
            self.model.to(device)
        return self

    def eval(self) -> "GuardianModel":
        """Set model to evaluation mode."""
        if self.model:
            self.model.eval()
        return self

    def train(self) -> "GuardianModel":
        """Set model to training mode."""
        if self.model:
            self.model.train()
        return self

    def __call__(self, *args, **kwargs):
        """Forward pass through the model."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return self.model(*args, **kwargs)
