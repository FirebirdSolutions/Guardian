"""
Guardian LLM Scripts

CLI tools for training data preparation, model training, and batch processing.

Available scripts:
- train: Train the Guardian LLM model
- prepare_data: Prepare and normalize training data
- process_external: Process external datasets (Mendeley, SWMH)
- batch_submit: Submit batch jobs to Anthropic API
- batch_download: Download and process batch results
- normalize: Normalize training data for consistent tool calling
- generate_variations: Generate training data variations via batch API
"""

__all__ = [
    "train",
    "prepare_data",
    "process_external",
    "batch_submit",
    "batch_download",
    "normalize",
    "generate_variations",
]
