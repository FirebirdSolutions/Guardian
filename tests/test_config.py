"""Tests for the Guardian LLM configuration system."""

import pytest
import json
import tempfile
from pathlib import Path

from guardian_llm.config import (
    ModelSize,
    BaseModelType,
    GuardianConfig,
    TrainingConfig,
    InferenceConfig,
    ExportConfig,
)


class TestModelSize:
    """Tests for ModelSize enum."""

    def test_all_sizes_defined(self):
        """Test all expected model sizes are defined."""
        expected = ["TINY", "SMALL", "MEDIUM", "LARGE"]
        for size in expected:
            assert hasattr(ModelSize, size)

    def test_size_values(self):
        """Test model size values."""
        assert ModelSize.TINY.value == "tiny"
        assert ModelSize.SMALL.value == "small"
        assert ModelSize.MEDIUM.value == "medium"
        assert ModelSize.LARGE.value == "large"


class TestBaseModelType:
    """Tests for BaseModelType enum."""

    def test_model_types_defined(self):
        """Test supported model types are defined."""
        assert hasattr(BaseModelType, "QWEN2_5")
        assert hasattr(BaseModelType, "LLAMA3")
        assert hasattr(BaseModelType, "MISTRAL")


class TestGuardianConfig:
    """Tests for GuardianConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = GuardianConfig()

        assert config.model_size == ModelSize.LARGE
        assert config.base_model_type == BaseModelType.QWEN2_5
        assert "Qwen" in config.base_model_id
        assert config.max_seq_length == 2048

    def test_lora_config(self):
        """Test LoRA configuration defaults."""
        config = GuardianConfig()

        assert config.lora_r == 64
        assert config.lora_alpha == 32
        assert config.lora_dropout == 0.05
        assert len(config.lora_target_modules) > 0
        assert "q_proj" in config.lora_target_modules

    def test_quantization_config(self):
        """Test quantization defaults."""
        config = GuardianConfig()

        assert config.load_in_4bit is True
        assert config.load_in_8bit is False
        assert config.bnb_4bit_quant_type == "nf4"
        assert config.bnb_4bit_use_double_quant is True

    def test_crisis_categories(self):
        """Test crisis categories are defined."""
        config = GuardianConfig()

        assert "suicide_ideation" in config.crisis_categories
        assert "self_harm" in config.crisis_categories
        assert "domestic_violence" in config.crisis_categories
        assert "false_positive" in config.crisis_categories

    def test_risk_levels(self):
        """Test risk levels are defined."""
        config = GuardianConfig()

        assert config.risk_levels == ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    def test_system_prompt_contains_resources(self):
        """Test system prompt contains crisis resources."""
        config = GuardianConfig()

        assert "111" in config.system_prompt
        assert "1737" in config.system_prompt
        assert "FAKE" in config.system_prompt

    def test_from_model_size_tiny(self):
        """Test creating config for tiny model."""
        config = GuardianConfig.from_model_size(ModelSize.TINY)

        assert config.model_size == ModelSize.TINY
        assert "0.5B" in config.base_model_id
        assert config.lora_r == 16
        assert config.max_seq_length == 1024

    def test_from_model_size_small(self):
        """Test creating config for small model."""
        config = GuardianConfig.from_model_size(ModelSize.SMALL)

        assert config.model_size == ModelSize.SMALL
        assert "1.5B" in config.base_model_id
        assert config.lora_r == 32

    def test_from_model_size_medium(self):
        """Test creating config for medium model."""
        config = GuardianConfig.from_model_size(ModelSize.MEDIUM)

        assert config.model_size == ModelSize.MEDIUM
        assert "3B" in config.base_model_id
        assert config.lora_r == 48

    def test_from_model_size_large(self):
        """Test creating config for large model."""
        config = GuardianConfig.from_model_size(ModelSize.LARGE)

        assert config.model_size == ModelSize.LARGE
        assert "7B" in config.base_model_id
        assert config.lora_r == 64

    def test_to_json_and_from_json(self):
        """Test saving and loading config from JSON."""
        config = GuardianConfig.from_model_size(ModelSize.SMALL)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            config.to_json(str(path))

            # Verify file exists and is valid JSON
            assert path.exists()
            with open(path) as f:
                data = json.load(f)
            assert data["model_size"] == "small"

            # Load back
            loaded = GuardianConfig.from_json(str(path))
            assert loaded.model_size == ModelSize.SMALL
            assert loaded.base_model_id == config.base_model_id


class TestTrainingConfig:
    """Tests for TrainingConfig."""

    def test_default_config(self):
        """Test default training configuration."""
        config = TrainingConfig()

        assert config.num_epochs == 20
        assert config.batch_size == 24
        assert config.learning_rate == 5e-5
        assert config.warmup_steps == 10

    def test_validation_split(self):
        """Test validation split default."""
        config = TrainingConfig()
        assert config.validation_split == 0.1

    def test_optimizer_settings(self):
        """Test optimizer settings."""
        config = TrainingConfig()

        assert config.optimizer == "adamw_torch"
        assert config.weight_decay == 0.01
        assert config.max_grad_norm == 1.0

    def test_precision_settings(self):
        """Test precision settings."""
        config = TrainingConfig()

        assert config.bf16 is True
        assert config.fp16 is False
        assert config.tf32 is True

    def test_checkpoint_settings(self):
        """Test checkpoint settings."""
        config = TrainingConfig()

        assert config.save_strategy == "epoch"
        assert config.save_total_limit == 5
        assert config.load_best_model_at_end is True

    def test_early_stopping(self):
        """Test early stopping settings."""
        config = TrainingConfig()

        assert config.early_stopping_patience == 3
        assert config.early_stopping_threshold == 0.01

    def test_guardian_specific_settings(self):
        """Test Guardian-specific training settings."""
        config = TrainingConfig()

        assert config.crisis_weight_multiplier == 2.0
        assert config.balance_risk_levels is True

    def test_reproducibility_settings(self):
        """Test reproducibility settings."""
        config = TrainingConfig()

        assert config.seed == 42
        assert config.data_seed == 42

    def test_to_json_and_from_json(self):
        """Test saving and loading training config."""
        config = TrainingConfig(num_epochs=10, batch_size=16)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "training.json"
            config.to_json(str(path))

            loaded = TrainingConfig.from_json(str(path))
            assert loaded.num_epochs == 10
            assert loaded.batch_size == 16


class TestInferenceConfig:
    """Tests for InferenceConfig."""

    def test_default_config(self):
        """Test default inference configuration."""
        config = InferenceConfig()

        assert config.max_new_tokens == 512
        assert config.temperature == 0.1  # Low for crisis responses
        assert config.top_p == 0.9
        assert config.do_sample is True

    def test_streaming_settings(self):
        """Test streaming settings."""
        config = InferenceConfig()

        assert config.stream is True
        assert config.stream_chunk_size == 1

    def test_guardian_specific_settings(self):
        """Test Guardian-specific inference settings."""
        config = InferenceConfig()

        assert config.enforce_structured_output is True
        assert config.validate_resources is True
        assert config.max_response_time_ms == 5000


class TestExportConfig:
    """Tests for ExportConfig."""

    def test_default_config(self):
        """Test default export configuration."""
        config = ExportConfig()

        assert config.export_gguf is True
        assert config.export_safetensors is True
        assert config.merge_lora is True

    def test_gguf_settings(self):
        """Test GGUF export settings."""
        config = ExportConfig()

        assert config.gguf_quantization == "q4_k_m"

    def test_onnx_settings(self):
        """Test ONNX export settings."""
        config = ExportConfig()

        assert config.export_onnx is False  # Off by default
        assert config.onnx_opset == 14

    def test_output_directory(self):
        """Test export output directory."""
        config = ExportConfig()

        assert config.export_dir == "./guardian-export"


class TestConfigIntegration:
    """Integration tests for config classes."""

    def test_configs_work_together(self):
        """Test that all configs can be created together."""
        guardian_config = GuardianConfig.from_model_size(ModelSize.SMALL)
        training_config = TrainingConfig()
        inference_config = InferenceConfig()
        export_config = ExportConfig()

        # All should be created successfully
        assert guardian_config is not None
        assert training_config is not None
        assert inference_config is not None
        assert export_config is not None

    def test_crisis_categories_match_risk_levels(self):
        """Test crisis categories have appropriate coverage."""
        config = GuardianConfig()

        # Should have categories for false positives
        assert "false_positive" in config.crisis_categories

        # Should have LOW as a risk level
        assert "LOW" in config.risk_levels
