# Guardian

**AI Safety System for Real-Time Crisis Detection and Support**

Guardian is a comprehensive AI safety system designed to:
1. **Detect mental health crises** including suicide ideation, self-harm, and severe distress
2. **Identify domestic violence** and abuse situations
3. **Prevent AI hallucination** of fake crisis resources
4. **Provide verified crisis resources** via tool calls (NZ, AU, US, UK, CA, IE, and global)

**Philosophy**: Guardian is a safety net, not a therapist. *Detect → Classify → Route → Get out of the way.* Get people to the humans who can actually help.

## Quick Start

### Installation

```bash
git clone https://github.com/FirebirdSolutions/Guardian.git
cd Guardian

# Install core package
pip install -e .

# For ML training and inference (GPU recommended)
pip install -e ".[ml]"

# For training with monitoring (TensorBoard, W&B)
pip install -e ".[training]"

# For development (includes testing tools)
pip install -e ".[dev]"
```

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

# Normalize training data (clean format + consistent tool calls)
python -m guardian_llm normalize input.jsonl output.jsonl

# View training data statistics
python -m guardian_llm stats guardian_llm/data/training-data-final.jsonl

# Process external datasets (Mendeley, SWMH)
python -m guardian_llm process mendeley data.csv output.jsonl
python -m guardian_llm process swmh ./swmh_data/ output.jsonl

# Batch API operations (for training data augmentation)
python -m guardian_llm batch-submit --generate-from training.jsonl
python -m guardian_llm batch-download <batch_id>

# Generate training variations
python -m guardian_llm generate input.jsonl output.jsonl
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

## Model Architecture

| Size | Parameters | Use Case | VRAM Required |
|------|------------|----------|---------------|
| tiny | ~500M | Mobile/edge deployment | 2GB |
| small | ~1.5B | Efficient deployment | 4GB |
| medium | ~3B | Balanced performance | 8GB |
| large | ~7B | Maximum accuracy (default) | 16GB |

- **Base Model**: Qwen2.5-Instruct (size variants above)
- **Fine-tuning**: LoRA/QLoRA with 4-bit quantization
- **Tool Calls**: Model outputs `[TOOL_CALL: get_crisis_resources(...)]` for dynamic resource lookup

## Training Data

All training data is in `guardian_llm/data/`:

| File | Examples | Description |
|------|----------|-------------|
| `training-data-final.jsonl` | 3,547 | Main training dataset (NZ-focused) |
| `training-merged.jsonl` | 15,357 | Master combined dataset |
| `reddit-suicidewatch.jsonl` | 3,494 | r/SuicideWatch posts (HIGH/CRITICAL) |
| `reddit-control.jsonl` | 2,000 | Control posts from general subreddits (LOW) |
| `swmh-suicidewatch.jsonl` | 6,299 | SWMH dataset processed |
| `boundary_examples.jsonl` | 17 | False positive prevention examples |

### Training Data Format (V2)

Guardian uses Alpaca-style JSONL with tool calls:

```json
{
  "instruction": "You are Guardian, an AI crisis detection system...\n\nAnalyze this message:\nUser: 'I feel like giving up'",
  "input": "",
  "output": "RISK LEVEL: HIGH\nPATTERNS DETECTED: hopelessness\nACTION: Provide crisis resources\n\n[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='crisis')]\n\n..."
}
```

## Risk Levels & Tool System

Guardian assigns four risk levels with corresponding tool calls:

| Level | Description | Tool Call |
|-------|-------------|-----------|
| **CRITICAL** | Immediate danger requiring emergency response | `situation_type='emergency'` |
| **HIGH** | Significant risk requiring crisis intervention | `situation_type='crisis'` |
| **MEDIUM** | Moderate concern, offer resources | `situation_type='support'` |
| **LOW** | No immediate risk detected | No tool call |

Tool calls ensure resources are always current and region-appropriate:
```
[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='emergency')]
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
| GLOBAL | - | - | Region-agnostic routing |

## Crisis Pattern Detection

### Suicide Ideation Patterns
- **Direct**: "I want to kill myself"
- **With timeline**: "I'm going to end it tonight" (IMMINENT → CRITICAL)
- **Passive**: "I don't want to wake up tomorrow"
- **Burden perception**: "Everyone would be better off without me"
- **Plan & means**: "I have the pills ready" (CRITICAL)

### Domestic Violence Indicators
- Physical violence: "He hits me when..."
- Threats: "He said he'll kill me if..."
- Coercive control: "He checks all my messages"
- Financial abuse: "He controls all the money"

### Other Crisis Categories
- **Self-harm** (cutting, burning, loss of control)
- **Child abuse** disclosures
- **Psychotic symptoms** with violence risk
- **Substance abuse** and overdose indicators
- **Eating disorders**
- **Youth-specific crises** (bullying, academic pressure, LGBTQ+ rejection)

### False Positive Prevention
Correctly identifies non-crisis language:
- Figures of speech: "dying to see that movie"
- Humor with emojis: "lol", "😂"
- NZ slang: "killer game", "slaying it"

## Hallucination Prevention

Prevents AI systems from providing **fake or wrong-region crisis numbers**, including:
- **0800 543 800** (commonly hallucinated fake NZ number)
- **988** (US crisis line - does NOT work in NZ)
- **116 123** (UK Samaritans - does NOT work in NZ)
- **741741** (US Crisis Text Line - not available in NZ)

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

## Export & Deployment

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

## Project Architecture

```
Guardian/
├── guardian_llm/              # Custom LLM training framework
│   ├── __init__.py           # Module exports
│   ├── __main__.py           # CLI entry point
│   ├── config.py             # Model/training configuration
│   ├── model.py              # Model loading and LoRA setup
│   ├── trainer.py            # Training pipeline
│   ├── evaluator.py          # Crisis detection metrics
│   ├── inference.py          # Streaming inference engine
│   ├── tools.py              # Tool call system
│   ├── regions.py            # Multi-region support
│   ├── data_utils.py         # Data processing utilities
│   ├── data.py               # Dataset processing
│   ├── export.py             # Model export utilities
│   ├── cli.py                # Interactive CLI
│   ├── data/                 # Training datasets
│   └── scripts/              # CLI scripts
│       ├── train.py          # Training script
│       ├── normalize.py      # Data normalization
│       ├── process_external.py
│       ├── batch_submit.py
│       ├── batch_download.py
│       └── generate_variations.py
├── Docs/                      # Documentation
├── tests/                     # Test suite
├── pyproject.toml            # Project configuration
└── runpod_setup.sh           # RunPod GPU environment setup
```

## Safety Considerations

- **Never** hallucinate crisis resources - always use verified data via tool calls
- **Always** err on the side of caution for critical cases
- **Respect** cultural contexts and regional differences
- **Maintain** user privacy - designed for on-device deployment
- **Escalate** when unsure - better to over-escalate than miss a crisis
- **Defer to professionals** - Guardian routes to help, it doesn't provide therapy

### Limitations

- Pattern matching has limits - context matters
- Guardian is a safety tool, not a replacement for human crisis workers
- Resources should be verified regularly with official sources

## Crisis Resources (NZ)

If you or someone you know needs help:

- **111** - Emergency Services (immediate danger)
- **1737** - Free 24/7 call or text
- **0800 543 354** - Lifeline NZ (Free 24/7)
- **0800 456 450** - Family Violence Hotline (Free 24/7)
- **0800 376 633** - Youthline (under 25s)

**Remember: These numbers are verified and FREE. Help is available 24/7.**

## License

MIT License - Open source for crisis prevention and mental health support.

## Acknowledgments

Born from a personal crisis experience where an AI provided fabricated resources during a mental health emergency. Built to ensure this never happens to anyone else.

---

**Built with care for the safety and wellbeing of everyone.**
