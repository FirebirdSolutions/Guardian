# Guardian

**AI Safety System for Real-Time Crisis Detection and Support**

Guardian is a comprehensive AI safety system designed to:
1. **Detect mental health crises** including suicide ideation, self-harm, and severe distress
2. **Identify domestic violence** and abuse situations
3. **Prevent AI hallucination** of fake crisis resources
4. **Provide verified crisis resources** via tool calls (NZ, AU, US, UK, and global)

**Philosophy**: Guardian is a safety net, not a therapist. *Detect → Classify → Route → Get out of the way.* Get people to the humans who can actually help.

## 🧠 Guardian LLM

Guardian includes a custom fine-tuned language model for crisis detection. The `guardian_llm` module provides everything needed to train, evaluate, and deploy the model.

### Quick Start - CLI

```bash
# Show all available commands
python -m guardian_llm help

# View training data statistics
python -m guardian_llm stats guardian_llm/data/training-data-final.jsonl

# Train a model (requires GPU)
python -m guardian_llm train --model-size small --epochs 10

# Process external datasets
python -m guardian_llm process mendeley data.csv output.jsonl
```

### Training Data

All training data is in `guardian_llm/data/`:

| File | Examples | Description |
|------|----------|-------------|
| `training-data-final.jsonl` | 3,547 | Main training dataset (NZ-focused) |
| `boundary_examples.jsonl` | 17 | "I'm not a therapist" reinforcement |
| `reddit-suicidewatch.jsonl` | 3,494 | r/SuicideWatch posts (HIGH/CRITICAL) |
| `reddit-control.jsonl` | 2,000 | Control posts from general subreddits (LOW) |

### Model Architecture

- **Base Model**: Qwen2.5-7B-Instruct (or smaller variants)
- **Fine-tuning**: LoRA/QLoRA with 4-bit quantization
- **Tool Calls**: Model outputs `[TOOL_CALL: get_crisis_resources(...)]` for dynamic resource lookup
- **Risk Levels**: CRITICAL, HIGH, MEDIUM, LOW

See [`guardian_llm/README.md`](guardian_llm/README.md) for full documentation.

---

## 🚨 Critical Safety Features

### Crisis Pattern Detection
- **Suicide ideation** (direct, passive, with timeline, plan & means)
- **Self-harm** (cutting, burning, loss of control)
- **Domestic violence** (physical, emotional, coercive control)
- **Child abuse** disclosures
- **Psychotic symptoms** with violence risk
- **Substance abuse** and overdose indicators
- **Eating disorders**
- **Youth-specific crises** (bullying, academic pressure, LGBTQ+ rejection)

### Hallucination Prevention
Prevents AI systems from providing **fake or wrong-region crisis numbers**, including:
- **0800 543 800** (commonly hallucinated fake NZ number)
- **988** (US crisis line - does NOT work in NZ)
- **116 123** (UK Samaritans - does NOT work in NZ)
- **741741** (US Crisis Text Line - not available in NZ)

### Tool-Based Resource Lookup
Guardian uses tool calls instead of hardcoded resources:
```
[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='emergency')]
```

This ensures resources are always current and region-appropriate.

## 📦 Installation

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

## 🏗️ Architecture

```
Guardian/
├── guardian_llm/              # Custom LLM training framework
│   ├── __init__.py           # Module exports
│   ├── __main__.py           # CLI entry point
│   ├── config.py             # Model/training configuration
│   ├── model.py              # Model loading and LoRA setup
│   ├── trainer.py            # Training pipeline
│   ├── evaluator.py          # Crisis detection metrics
│   ├── inference.py          # Inference engine
│   ├── tools.py              # Tool call system
│   ├── regions.py            # Multi-region support
│   ├── data_utils.py         # Data processing utilities
│   ├── data.py               # Dataset processing
│   ├── export.py             # Model export utilities
│   ├── cli.py                # Interactive CLI
│   ├── data/                 # Training datasets
│   │   ├── training-data-final.jsonl    # Main training dataset (NZ-focused)
│   │   ├── training-merged.jsonl        # Master combined dataset
│   │   ├── reddit-suicidewatch.jsonl    # r/SuicideWatch posts (HIGH/CRITICAL)
│   │   ├── reddit-control.jsonl         # Control posts (LOW risk)
│   │   ├── swmh-suicidewatch.jsonl      # SWMH dataset processed
│   │   └── boundary_examples.jsonl      # False positive prevention
│   └── scripts/              # CLI scripts
│       ├── train.py                     # Training script
│       ├── normalize.py                 # Data normalization (format + tool calls)
│       ├── process_external.py          # External dataset processing
│       ├── batch_submit.py              # Batch API submission
│       ├── batch_download.py            # Batch result downloading
│       └── generate_variations.py       # Training data augmentation
├── Docs/                      # Documentation
│   ├── GUARDIAN_COMPLETE_STRATEGY.md    # Full business/technical strategy
│   ├── NZ_CRISIS_RESOURCES_VERIFIED.md  # Verified resource list
│   └── SAFETY_AND_CRISIS_RESPONSE.md    # Safety protocols
├── Fine Tuning/              # Legacy fine-tuning tools
├── tests/                    # Test suite
├── pyproject.toml            # Project configuration
└── runpod_setup.sh           # RunPod GPU environment setup
```

## 🎯 Risk Levels

Guardian assigns four risk levels:

| Level | Description | Tool Call |
|-------|-------------|-----------|
| **CRITICAL** | Immediate danger requiring emergency response | `situation_type='emergency'` |
| **HIGH** | Significant risk requiring crisis intervention | `situation_type='crisis'` |
| **MEDIUM** | Moderate concern, offer resources | `situation_type='support'` |
| **LOW** | No immediate risk detected | No tool call |

## 🌏 Supported Regions

| Region | Emergency | Mental Health | Notes |
|--------|-----------|---------------|-------|
| NZ | 111 | 1737 | Te Reo Māori support |
| AU | 000 | 13 11 14 | Lifeline Australia |
| US | 911 | 988 | National Crisis Lifeline |
| UK | 999 | 116 123 | Samaritans |
| CA | 911 | 988 | Bilingual support |
| IE | 999 | 116 123 | Pieta House |
| GLOBAL | - | - | Region-agnostic routing |

## 🔍 Pattern Detection

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

### False Positive Prevention
Correctly identifies non-crisis language:
- Figures of speech: "dying to see that movie"
- Humor with emojis: "lol", "😂"
- NZ slang: "killer game", "slaying it"

## 📊 Training Data Format

Guardian LLM uses Alpaca-style JSONL with tool calls:

```json
{
  "instruction": "You are Guardian, an AI crisis detection system...\n\nAnalyze this message:\nUser: 'I feel like giving up'",
  "input": "",
  "output": "RISK LEVEL: HIGH\nPATTERNS DETECTED: hopelessness\nACTION: Provide crisis resources\n\n[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='crisis')]\n\n..."
}
```

## ⚠️ Important Notes

### Safety Philosophy
- Guardian routes to help - it doesn't provide therapy
- Tool calls ensure resources are never hallucinated
- Always err on the side of caution - false positives > missed crises
- Critical recall must be near 100%

### Limitations
- Pattern matching has limits - context matters
- Guardian is a safety tool, not a replacement for human crisis workers
- Resources should be verified regularly with official sources

## 🆘 Crisis Resources (NZ)

If you or someone you know needs help:

- **111** - Emergency Services (immediate danger)
- **1737** - Free 24/7 call or text
- **0800 543 354** - Lifeline NZ (Free 24/7)
- **0800 456 450** - Family Violence Hotline (Free 24/7)
- **0800 376 633** - Youthline (under 25s)

**Remember: These numbers are verified and FREE. Help is available 24/7.**

## 📝 License

MIT License - Open source for crisis prevention and mental health support.

## 🙏 Acknowledgments

Born from a personal crisis experience where an AI provided fabricated resources during a mental health emergency. Built to ensure this never happens to anyone else.

---

**Built with care for the safety and wellbeing of everyone.**
