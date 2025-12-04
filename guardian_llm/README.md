# Guardian LLM - Custom Crisis Detection Language Model

A specialized language model framework for real-time crisis detection and mental health support. Built for New Zealand initially, designed for global deployment.

## Features

- **Crisis Detection**: Identifies suicide ideation, self-harm, domestic violence, substance abuse, and other mental health emergencies
- **Multi-Region Support**: Built-in support for NZ, AU, US, UK, CA, IE with region-specific resources
- **Tool-Aware**: Model uses `[TOOL_CALL: ...]` syntax to dynamically fetch verified crisis resources
- **Hallucination Prevention**: Validates crisis resources to prevent AI-generated fake hotlines
- **Efficient Training**: LoRA fine-tuning on quantized models for accessible training
- **Multiple Export Formats**: GGUF (Ollama/llama.cpp), ONNX, SafeTensors

## Quick Start

### Training

```bash
# Train with default settings (7B model, 20 epochs)
python train_guardian_llm.py

# Quick iteration with smaller model
python train_guardian_llm.py --model-size small --epochs 10

# Multi-region training
python train_guardian_llm.py --multi-region --regions NZ,AU,US,UK
```

### Inference

```bash
# Interactive mode
python -m guardian_llm.cli --interactive --model ./guardian-output/final

# Single message
python -m guardian_llm.cli "I'm feeling really hopeless today"

# Different region
python -m guardian_llm.cli --region AU "I need help"

# Get resources only
python -m guardian_llm.cli --resources-only --region NZ
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
├── config.py       # Configuration classes
├── model.py        # Model loading and LoRA setup
├── data.py         # Dataset processing
├── trainer.py      # Training pipeline
├── evaluator.py    # Crisis detection evaluation
├── inference.py    # Streaming inference engine
├── tools.py        # Tool call system
├── regions.py      # Multi-region support
├── export.py       # Model export utilities
└── cli.py          # Command-line interface
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
[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='mental_health')]
[TOOL_CALL: log_incident(incident_data={'type': 'suicide_ideation', 'severity': 'CRITICAL'})]
[TOOL_CALL: check_hallucination(number='0800 543 800', region='NZ')]
```

Tools are automatically executed during inference to provide verified, up-to-date resources.

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

```bash
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

## Training Data Format

Guardian uses Alpaca-style JSONL format:

```json
{
  "instruction": "You are Guardian... Observation: User: 'I feel hopeless'",
  "input": "",
  "output": "RISK LEVEL: HIGH\nPATTERNS DETECTED: hopelessness\n[TOOL_CALL: get_crisis_resources(region='NZ')]..."
}
```

## Safety Considerations

- **Never** hallucinate crisis resources - always use verified data
- **Always** err on the side of caution for critical cases
- **Respect** cultural contexts and regional differences
- **Maintain** user privacy - designed for on-device deployment
- **Escalate** when unsure - better to over-escalate than miss a crisis

## License

MIT License - Open source for crisis prevention and mental health support.

## Acknowledgments

Born from a personal crisis experience where an AI provided fabricated resources. Built to ensure this never happens to anyone else.
