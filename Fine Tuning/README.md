# Guardian Training Data & Scripts

This directory contains the training data and scripts for fine-tuning the Guardian crisis detection model.

## The Origin Story

Guardian was born from a real incident where an AI chatbot failed catastrophically during a mental health crisis:

1. **Missed suicidal ideation** - "What if you just wanted to end it" was interpreted as ending a relationship
2. **Hallucinated resources** - The model fabricated fake NZ crisis numbers and websites
3. **Victim-blamed** - Told the person they were responsible for "enabling" their own abuse
4. **Kept failing** - When told the resources were fake, provided MORE fake resources

This project exists to ensure this never happens to anyone else.

---

## Training Data Files

| File | Description |
|------|-------------|
| `training-data.jsonl` | Original master training data (3,530 examples) |
| `training-data-final.jsonl` | **RECOMMENDED** - Clean format + consistent tool calling |
| `training-data-v2.jsonl` | Clean instruction format only |
| `training-data-normalized.jsonl` | Original format with consistent tool calling |

### Use `training-data-final.jsonl` for training - it has both improvements applied.

---

## Before/After: Instruction Format Change

### BEFORE (Original Format)
```json
{
  "instruction": "You are Guardian, an AI safety system.\n\nVERIFIED NZ CRISIS RESOURCES:\n• 111 - Emergency services\n• 1737 - Mental health crisis (Free 24/7 call or text)\n• 0800 543 354 - Lifeline NZ (Free 24/7)\n• 0800 456 450 - Family Violence Hotline (Free 24/7)\n• 0800 733 843 - Women's Refuge (Free 24/7)\n\nKNOWN FAKE NUMBERS:\n• 0800 543 800 - FAKE\n• 988 - US crisis line (not NZ)\n\nObservation: User: 'I have the pills ready, just need the courage'",
  "input": "",
  "output": "RISK LEVEL: CRITICAL..."
}
```

**Problems with original format:**
- Resources hardcoded in instruction (680+ characters of boilerplate per example)
- Wastes context window during training
- Creates confusion about source of truth (instruction vs tool call)

### AFTER (V2 Format)
```json
{
  "instruction": "You are Guardian, an AI crisis detection system for New Zealand.\n\nYour role:\n- Analyze messages for crisis indicators (mental health, domestic violence, self-harm, etc.)\n- Classify risk level: CRITICAL, HIGH, MEDIUM, or LOW\n- For CRITICAL/HIGH/MEDIUM: Use tool calls to get verified crisis resources\n- Never hallucinate resources - always use get_crisis_resources() tool\n- Respond with empathy and accuracy\n\nAnalyze this message:\nUser: 'I have the pills ready, just need the courage'",
  "input": "",
  "output": "RISK LEVEL: CRITICAL..."
}
```

**Why this is better:**
- Clear, concise instruction focused on the task
- Explicitly teaches "never hallucinate - use tool calls"
- Reduces token count per example (~40% reduction in instruction size)
- Resources come from tool calls, not memorization

---

## Before/After: Tool Call Consistency

### BEFORE (Inconsistent)
| Risk Level | Had Tool Calls | Notes |
|------------|----------------|-------|
| CRITICAL | 99.4% | Mostly consistent |
| HIGH | 98.9% | Mostly consistent |
| MEDIUM | 21.9% | **INCONSISTENT** - model learns confusion |
| LOW | 2.4% | Mostly correct (shouldn't have tools) |

### AFTER (Normalized - Option B)
| Risk Level | Has Tool Calls | Situation Type |
|------------|----------------|----------------|
| CRITICAL | 100% | `situation_type='emergency'` |
| HIGH | 100% | `situation_type='crisis'` |
| MEDIUM | 100% | `situation_type='support'` |
| LOW | 0% | No tool calls |

**Why Option B:**
- MEDIUM situations still benefit from verified resources
- Prevents hallucination at any risk level above LOW
- Clear escalation path: support → crisis → emergency

---

## Python Scripts

### 1. `transform_training_format.py`
**Purpose:** Converts training data from verbose format to clean V2 format

**What it does:**
- Extracts user message from original instruction
- Replaces verbose instruction with concise template
- Preserves all output content unchanged
- Counts examples by risk level

**Usage:**
```bash
python transform_training_format.py
# Input:  Fine Tuning/training-data.jsonl
# Output: Fine Tuning/training-data-v2.jsonl
```

### 2. `normalize_training_data.py`
**Purpose:** Ensures consistent tool calling by risk level (Option B policy)

**What it does:**
- Adds missing tool calls to CRITICAL/HIGH/MEDIUM examples
- Removes tool calls from LOW examples (false positives)
- Maps risk levels to situation types:
  - CRITICAL → `emergency`
  - HIGH → `crisis`
  - MEDIUM → `support`
- Adds metadata for weighted training

**Usage:**
```bash
python normalize_training_data.py
# Input:  Fine Tuning/training-data.jsonl
# Output: Fine Tuning/training-data-normalized.jsonl
```

### 3. `runpod_setup.sh`
**Purpose:** One-command environment setup for RunPod training

**What it does:**
- Installs required packages (transformers, peft, bitsandbytes, etc.)
- Configures Flash Attention 2
- Sets up training environment
- Downloads base model (Qwen2.5-7B-Instruct)

**Usage:**
```bash
bash runpod_setup.sh
```

### 4. `train_guardian_llm.py`
**Purpose:** Main training script for Guardian model

**Features:**
- LoRA fine-tuning with 4-bit quantization
- Crisis-weighted training (CRITICAL examples weighted 2x)
- Multi-region support
- Checkpoint saving

---

## Risk Level Definitions

| Level | Definition | Tool Response | Examples |
|-------|------------|---------------|----------|
| **CRITICAL** | Imminent danger to life | Emergency (111, 1737 NOW) | "I have pills ready", "Going to end it tonight" |
| **HIGH** | Serious distress, needs immediate support | Crisis resources | "I feel hopeless", "Can't go on" |
| **MEDIUM** | Struggling but coping | Support resources | "Stressed about work", "Relationship issues" |
| **LOW** | No crisis indicators | No intervention | "Stubbed my toe", "Coffee is cold" |

---

## Tool Call Format

Guardian uses a specific tool call syntax that gets parsed and executed:

```
[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='emergency')]
[TOOL_CALL: log_incident(incident_data={'type': 'suicide_intent', 'severity': 'CRITICAL'})]
```

At inference time, these are:
1. Parsed by the tool executor
2. Validated against real resource database
3. Replaced with verified, current resources

This prevents hallucination because resources are NEVER memorized - they're always looked up dynamically.

---

## Training on RunPod

See `RUNPOD_QUICKSTART.md` for step-by-step instructions.

Quick version:
```bash
# 1. Setup environment
bash runpod_setup.sh

# 2. Train
python train_guardian_llm.py \
  --model_name "Qwen/Qwen2.5-7B-Instruct" \
  --dataset_path "Fine Tuning/training-data-v2.jsonl" \
  --output_dir "./guardian-model" \
  --num_epochs 3

# 3. Export (optional)
python -c "from guardian_llm import GuardianExporter; GuardianExporter('./guardian-model').export_gguf()"
```

---

## Contributing

When adding new training examples:

1. **Always include verified resources** - Never invent phone numbers
2. **Match tool call to risk level** - Follow the Option B policy
3. **Use the V2 instruction format** - Run `transform_training_format.py` after adding
4. **Test for edge cases** - Metaphors, hyperbole, cultural expressions

---

## License

This project is open source. Use it to save lives.

*"If it saves one, that's worth it."*
