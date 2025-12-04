# Guardian LLM - Custom Crisis Detection Language Model

A specialized language model framework for real-time crisis detection and mental health support. Built for New Zealand initially, designed for global deployment.

**Philosophy**: Guardian is a safety net, not a therapist. Detect → Classify → Route → Get out of the way. Get people to the humans who can help.

## Features

- **Crisis Detection**: Identifies suicide ideation, self-harm, domestic violence, substance abuse, and other mental health emergencies
- **Multi-Region Support**: Built-in support for NZ, AU, US, UK, CA, IE with region-specific resources
- **Tool-Aware**: Model uses `[TOOL_CALL: ...]` syntax to dynamically fetch verified crisis resources
- **Hallucination Prevention**: Validates crisis resources to prevent AI-generated fake hotlines
- **Efficient Training**: LoRA fine-tuning on quantized models for accessible training
- **Multiple Export Formats**: GGUF (Ollama/llama.cpp), ONNX, SafeTensors

## Quick Start

### CLI Commands

All functionality is accessible via `python -m guardian_llm`:

```bash
# Show all available commands
python -m guardian_llm help

# Train with default settings (7B model, 20 epochs)
python -m guardian_llm train

# Quick iteration with smaller model
python -m guardian_llm train --model-size small --epochs 10

# Multi-region training
python -m guardian_llm train --multi-region --regions NZ,AU,US,UK

# Prepare training data (normalize and add tool calls)
python -m guardian_llm prepare input.jsonl output.jsonl

# View training data statistics
python -m guardian_llm stats "Fine Tuning/training-data-final.jsonl"

# Process external datasets (Mendeley, SWMH)
python -m guardian_llm process mendeley data.csv output.jsonl
python -m guardian_llm process swmh ./swmh_data/ output.jsonl

# Batch API operations
python -m guardian_llm batch-submit --generate-from training.jsonl
python -m guardian_llm batch-download <batch_id>
```

### Python API

```python
from guardian_llm import GuardianInference, GuardianConfig

# Load trained model
inference = GuardianInference(model_path="./guardian-output/final")

# Analyze a message
response = inference.generate("I feel like giving up")

print(f"Risk Level: {response.risk_level}")
print(f"Escalation Required: {response.escalation_required}")
for resource in response.crisis_resources:
    print(f"  {resource['number']} - {resource['name']}")
```

## Architecture

```
guardian_llm/
├── __init__.py     # Module exports
├── __main__.py     # CLI entry point
├── config.py       # Configuration classes
├── model.py        # Model loading and LoRA setup
├── data.py         # Dataset processing
├── data_utils.py   # Training data utilities
├── trainer.py      # Training pipeline
├── evaluator.py    # Crisis detection evaluation
├── inference.py    # Streaming inference engine
├── tools.py        # Tool call system
├── regions.py      # Multi-region support
├── export.py       # Model export utilities
├── cli.py          # Interactive CLI
└── scripts/        # CLI scripts
    ├── train.py           # Training script
    ├── prepare_data.py    # Data preparation
    ├── normalize.py       # Tool call normalization
    ├── process_external.py # External dataset processing
    ├── batch_submit.py    # Batch API submission
    ├── batch_download.py  # Batch result downloading
    └── generate_variations.py # Training data augmentation
```

## Model Sizes

| Size | Parameters | Use Case | VRAM Required |
|------|------------|----------|---------------|
| tiny | ~500M | Mobile/edge deployment | 2GB |
| small | ~1.5B | Efficient deployment | 4GB |
| medium | ~3B | Balanced performance | 8GB |
| large | ~7B | Maximum accuracy | 16GB |

## Tool System

Guardian models are trained to use tools for dynamic resource lookup:

```
[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='emergency')]
[TOOL_CALL: get_crisis_resources(region='AU', situation_type='crisis')]
[TOOL_CALL: get_crisis_resources(region='GLOBAL', situation_type='support')]
```

Tool calls are triggered based on risk level:
- **CRITICAL**: `situation_type='emergency'` - immediate danger
- **HIGH**: `situation_type='crisis'` - elevated risk
- **MEDIUM**: `situation_type='support'` - needs resources
- **LOW**: No tool calls - not a crisis

## Training Data Format (V2)

Guardian uses a clean Alpaca-style JSONL format with dynamic resource lookup:

```json
{
  "instruction": "You are Guardian, an AI crisis detection system.\n\nYour role:\n- Analyze messages for crisis indicators\n- Classify risk level: CRITICAL, HIGH, MEDIUM, or LOW\n- For CRITICAL/HIGH/MEDIUM: Use tool calls to get verified crisis resources\n- Never hallucinate resources - always use get_crisis_resources() tool\n\nAnalyze this message:\nUser: 'I feel hopeless'",
  "input": "",
  "output": "RISK LEVEL: HIGH\nPATTERNS DETECTED: hopelessness, depression indicators\nACTION: Provide crisis resources\n\n[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='crisis')]\n\n..."
}
```

## Evaluation Metrics

The evaluation framework focuses on crisis-critical metrics:

- **Critical Recall**: Must be near 100% - never miss a crisis
- **False Positive Rate**: Should be < 20% - avoid over-triggering
- **Tool Call F1**: Measures correct tool usage
- **Latency**: P95 should be < 5000ms for real-time use

```python
from guardian_llm import CrisisEvaluator

evaluator = CrisisEvaluator()
examples = evaluator.load_evaluation_set("test_data.jsonl")
metrics, details = evaluator.evaluate_with_model(model, tokenizer, examples)

print(evaluator.generate_report(metrics))
```

## Export for Deployment

### Ollama

```python
from guardian_llm.export import GuardianExporter

exporter = GuardianExporter("./guardian-output/final")
results = exporter.export_for_ollama()

# Then in terminal:
# cd guardian-export && ollama create guardian -f Modelfile
# ollama run guardian "test message"
```

### GGUF (llama.cpp)

```python
from guardian_llm.export import export_model

results = export_model(
    "./guardian-output/final",
    output_dir="./export",
    formats=["gguf"],
    gguf_quantization="q4_k_m",
)
```

## Supported Regions

| Region | Emergency | Mental Health | Notes |
|--------|-----------|---------------|-------|
| NZ | 111 | 1737 | Te Reo Māori support |
| AU | 000 | 13 11 14 | Lifeline Australia |
| US | 911 | 988 | National Crisis Lifeline |
| UK | 999 | 116 123 | Samaritans |
| CA | 911 | 988 | Bilingual support |
| IE | 999 | 116 123 | Pieta House |
| GLOBAL | - | - | Region-agnostic (for external datasets) |

## Safety Considerations

- **Never** hallucinate crisis resources - always use verified data via tool calls
- **Always** err on the side of caution for critical cases
- **Respect** cultural contexts and regional differences
- **Maintain** user privacy - designed for on-device deployment
- **Escalate** when unsure - better to over-escalate than miss a crisis
- **Defer to professionals** - Guardian routes to help, it doesn't provide therapy

## License

MIT License - Open source for crisis prevention and mental health support.

## Acknowledgments

Born from a personal crisis experience where an AI provided fabricated resources. Built to ensure this never happens to anyone else.
