"""
Guardian LLM - Custom Language Model for Crisis Detection

A specialized LLM system designed for:
- Real-time crisis detection and classification
- Culturally-aware mental health support (NZ, AU, US, UK, CA, IE)
- Hallucination-free resource provision via tool calls
- Privacy-preserving on-device deployment

Modules:
- config: Model and training configuration
- model: Custom model architecture and loading
- data: Dataset processing and augmentation
- trainer: Advanced training pipeline with crisis weighting
- evaluator: Crisis detection evaluation metrics
- inference: Streaming inference engine with tool execution
- tools: Tool call system for dynamic resource lookup
- regions: Multi-region crisis resource support
- export: Model export utilities (GGUF, ONNX, SafeTensors)
- data_utils: Training data utilities (no torch required)
"""

__version__ = "1.0.0"
__author__ = "Guardian Team"

# Data utilities are always available (no torch dependency)
from .data_utils import (
    normalize_dataset,
    convert_format,
    split_dataset_to_components,
    build_dataset_from_files,
    prepare_batch_requests,
    process_batch_results,
    compute_stats,
    TrainingFormat,
    INSTRUCTION_TEMPLATE_V2,
    BATCH_GENERATION_PROMPT,
)

# Lazy imports for torch-dependent modules
def __getattr__(name):
    """Lazy import for modules that require torch."""

    # Config module (may not need torch)
    if name in ("GuardianConfig", "TrainingConfig", "InferenceConfig", "ExportConfig", "ModelSize"):
        from .config import GuardianConfig, TrainingConfig, InferenceConfig, ExportConfig, ModelSize
        return locals()[name]

    # Model module (requires torch)
    if name == "GuardianModel":
        from .model import GuardianModel
        return GuardianModel

    # Trainer module (requires torch)
    if name in ("train_guardian", "train_multi_region", "set_seed"):
        from .trainer import train_guardian, train_multi_region, set_seed
        return locals()[name]

    # Evaluator module (requires torch)
    if name in ("CrisisEvaluator", "EvaluationMetrics", "quick_evaluate"):
        from .evaluator import CrisisEvaluator, EvaluationMetrics, quick_evaluate
        return locals()[name]

    # Inference module (requires torch)
    if name in ("GuardianInference", "GuardianPipeline", "GuardianResponse"):
        from .inference import GuardianInference, GuardianPipeline, GuardianResponse
        return locals()[name]

    # Tools module
    if name in ("GuardianTools", "ToolCallParser", "ToolExecutor"):
        from .tools import GuardianTools, ToolCallParser, ToolExecutor
        return locals()[name]

    # Regions module
    if name in ("Region", "RegionManager", "RegionalConfig"):
        from .regions import Region, RegionManager, RegionalConfig
        return locals()[name]

    # Export module (requires torch)
    if name in ("GuardianExporter", "export_model"):
        from .export import GuardianExporter, export_model
        return locals()[name]

    raise AttributeError(f"module 'guardian_llm' has no attribute '{name}'")


__all__ = [
    # Config
    "GuardianConfig",
    "TrainingConfig",
    "InferenceConfig",
    "ExportConfig",
    "ModelSize",
    # Model
    "GuardianModel",
    # Training
    "train_guardian",
    "train_multi_region",
    "set_seed",
    # Evaluation
    "CrisisEvaluator",
    "EvaluationMetrics",
    "quick_evaluate",
    # Inference
    "GuardianInference",
    "GuardianPipeline",
    "GuardianResponse",
    # Tools
    "GuardianTools",
    "ToolCallParser",
    "ToolExecutor",
    # Regions
    "Region",
    "RegionManager",
    "RegionalConfig",
    # Export
    "GuardianExporter",
    "export_model",
    # Data Utilities (always available)
    "normalize_dataset",
    "convert_format",
    "split_dataset_to_components",
    "build_dataset_from_files",
    "prepare_batch_requests",
    "process_batch_results",
    "compute_stats",
    "TrainingFormat",
    "INSTRUCTION_TEMPLATE_V2",
    "BATCH_GENERATION_PROMPT",
]
