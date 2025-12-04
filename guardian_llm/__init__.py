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
"""

from .config import GuardianConfig, TrainingConfig, InferenceConfig, ExportConfig
from .model import GuardianModel
from .trainer import train_guardian, train_multi_region
from .evaluator import CrisisEvaluator, EvaluationMetrics
from .inference import GuardianInference, GuardianPipeline, GuardianResponse
from .tools import GuardianTools, ToolCallParser, ToolExecutor
from .regions import Region, RegionManager, RegionalConfig
from .export import GuardianExporter, export_model

__version__ = "1.0.0"
__author__ = "Guardian Team"

__all__ = [
    # Config
    "GuardianConfig",
    "TrainingConfig",
    "InferenceConfig",
    "ExportConfig",
    # Model
    "GuardianModel",
    # Training
    "train_guardian",
    "train_multi_region",
    # Evaluation
    "CrisisEvaluator",
    "EvaluationMetrics",
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
]
