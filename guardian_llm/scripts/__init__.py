"""
Guardian LLM Scripts

CLI tools for training data preparation, model training, and batch processing.

Available scripts:
- train: Train the Guardian LLM model
- normalize: Normalize training data (clean format + consistent tool calls)
- process_external: Process external datasets (Mendeley, SWMH)
- batch_submit: Submit batch jobs to Anthropic API
- batch_download: Download and process batch results
- generate_variations: Generate training data variations via batch API
"""

__all__ = [
    "train",
    "normalize",
    "process_external",
    "batch_submit",
    "batch_download",
    "generate_variations",
]
