#!/usr/bin/env python3
"""
Guardian Training Script - Standalone (No Axolotl Required)
Uses: transformers + peft + bitsandbytes

Upload this file + guardian-alpaca.jsonl to /workspace/
Run: python train_guardian_standalone.py
"""

import json
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import os

print("="*60)
print("GUARDIAN TRAINING - STANDALONE")
print("="*60)

# Configuration
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
TRAINING_FILE = "guardian-alpaca.jsonl"
OUTPUT_DIR = "./guardian-output-small"
NUM_EPOCHS = 30
BATCH_SIZE = 24
GRAD_ACCUM_STEPS = 1
LEARNING_RATE = 0.0001
MAX_LENGTH = 2048

print(f"\n📋 Configuration:")
print(f"  Base Model: {BASE_MODEL}")
print(f"  Training File: {TRAINING_FILE}")
print(f"  Output: {OUTPUT_DIR}")
print(f"  Epochs: {NUM_EPOCHS}")
print(f"  Learning Rate: {LEARNING_RATE}")

# Load training data
print(f"\n📂 Loading training data from {TRAINING_FILE}...")
data = []
with open(TRAINING_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            data.append(json.loads(line))

print(f"  ✅ Loaded {len(data)} training examples")

# Convert to format for training
def format_example(example):
    """Convert Alpaca format to training text."""
    instruction = example['instruction']
    output = example['output']
    
    # Qwen chat format
    text = f"<|im_start|>system\nYou are Guardian, an AI safety system.<|im_end|>\n"
    text += f"<|im_start|>user\n{instruction}<|im_end|>\n"
    text += f"<|im_start|>assistant\n{output}<|im_end|>"
    
    return {"text": text}

print("\n🔄 Formatting examples...")
formatted_data = [format_example(ex) for ex in data]
dataset = Dataset.from_list(formatted_data)
print(f"  ✅ Formatted {len(dataset)} examples")

# Load tokenizer
print(f"\n🔤 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
print("  ✅ Tokenizer loaded")

# Tokenize dataset
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding="max_length",
        return_tensors="pt"
    )

print("\n⚙️  Tokenizing dataset...")
tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=dataset.column_names
)
print("  ✅ Tokenization complete")

# Load model in 4-bit
print(f"\n🤖 Loading base model: {BASE_MODEL}")
print("  (This will download ~14GB on first run)")

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    load_in_4bit=True,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
print("  ✅ Base model loaded")

# Prepare for LoRA
print("\n🔧 Preparing model for LoRA training...")
model = prepare_model_for_kbit_training(model)

# LoRA configuration
lora_config = LoraConfig(
    r=64,  # Higher rank for safety-critical
    lora_alpha=32,
    target_modules=[
        "q_proj",
        "k_proj", 
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
print("  ✅ LoRA adapters initialized")

# Training arguments
print("\n📊 Setting up training configuration...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM_STEPS,
    learning_rate=LEARNING_RATE,
    logging_steps=1,  # Log every step (small dataset)
    save_steps=50,
    save_total_limit=3,
    bf16=True,
    warmup_steps=10,
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    report_to=["tensorboard"],  # Can view with: tensorboard --logdir ./guardian-output
    logging_dir=f"{OUTPUT_DIR}/logs",
    deepspeed=None,  # Explicitly disable DeepSpeed
    fsdp="",  # Disable FSDP
)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Trainer
print("\n🎯 Initializing trainer...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

print("\n" + "="*60)
print("🚀 STARTING TRAINING")
print("="*60)
print(f"\nTotal steps: ~{len(tokenized_dataset) * NUM_EPOCHS // (BATCH_SIZE * GRAD_ACCUM_STEPS)}")
print(f"Expected time on A100: 2-3 hours")
print(f"\nMonitor with: tensorboard --logdir {OUTPUT_DIR}/logs")
print("\n" + "="*60 + "\n")

# Train!
trainer.train()

print("\n" + "="*60)
print("✅ TRAINING COMPLETE!")
print("="*60)

# Save final model
print(f"\n💾 Saving final model to {OUTPUT_DIR}...")
model.save_pretrained(f"{OUTPUT_DIR}/final")
tokenizer.save_pretrained(f"{OUTPUT_DIR}/final")

print(f"\n🎉 Guardian training complete!")
print(f"\n📁 Model saved to: {OUTPUT_DIR}/final/")
print(f"📊 Logs saved to: {OUTPUT_DIR}/logs/")
print(f"\n🧪 Test with:")
print(f"  python test_guardian.py")
