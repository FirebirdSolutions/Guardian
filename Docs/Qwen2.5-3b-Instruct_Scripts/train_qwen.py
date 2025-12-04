#!/usr/bin/env python3
"""
Guardian Training Script - Standalone (No Axolotl Required)
Uses: transformers + peft + bitsandbytes

Upload this file + guardian-alpaca.jsonl to /workspace/
Run: python train_guardian_standalone.py
"""

import json
import torch
import numpy as np
import random
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
# Note: The `Dataset` import is modified below
from datasets import Dataset, load_dataset, DatasetDict
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import os

# ============================================
# SET RANDOM SEED FOR REPRODUCIBILITY
# ============================================
SEED = 13

torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)
torch.cuda.manual_seed_all(SEED)

# For full reproducibility (slightly slower)
# torch.backends.cudnn.deterministic = True
# torch.backends.cudnn.benchmark = False

print("="*60)
print("GUARDIAN TRAINING - STANDALONE")
print("="*60)
print(f"🌱 Random seed set to: {SEED}")

# Configuration
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
TRAINING_FILE = "training-data.jsonl"
OUTPUT_DIR = f"./guardian-qwen-output"
NUM_EPOCHS = 8
BATCH_SIZE = 48
GRAD_ACCUM_STEPS = 1
LEARNING_RATE = 5e-5
MAX_LENGTH = 2048
VALIDATION_SPLIT = 0.1 # <--- NEW: 10% for validation

print(f"\n📋 Configuration:")
print(f"  Base Model: {BASE_MODEL}")
print(f"  Training File: {TRAINING_FILE}")
print(f"  Output: {OUTPUT_DIR}")
print(f"  Epochs: {NUM_EPOCHS}")
print(f"  Learning Rate: {LEARNING_RATE}")
print(f"  Validation Split: {VALIDATION_SPLIT*100}%")


# Load training data (using simpler load_dataset functionality)
print(f"\n📂 Loading training data from {TRAINING_FILE}...")
# Assumes the file is a JSON Lines file
dataset = load_dataset('json', data_files=TRAINING_FILE)
# datasets library loads as a DatasetDict with 'train' key by default
dataset = dataset['train']

print(f"  ✅ Loaded {len(dataset)} training examples")

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
# Map the formatting function across the dataset
dataset = dataset.map(format_example, remove_columns=dataset.column_names)
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
    remove_columns=['text']
)
print("  ✅ Tokenization complete")

# --- NEW: Split the tokenized dataset into train and validation sets ---
print(f"\n✂️ Splitting dataset into training and validation sets ({100-VALIDATION_SPLIT*100}% train, {VALIDATION_SPLIT*100}% val)...")
split_datasets = tokenized_dataset.train_test_split(test_size=VALIDATION_SPLIT, seed=SEED)
train_dataset = split_datasets['train']
eval_dataset = split_datasets['test'] # 'test' key used for validation in Trainer
print(f"  ✅ Train size: {len(train_dataset)}, Validation size: {len(eval_dataset)}")


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
    logging_steps=1,
    save_steps=50,
    save_total_limit=20,
    bf16=True,
    warmup_steps=10,
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    report_to=["tensorboard"],
    logging_dir=f"{OUTPUT_DIR}/logs",

    # FIXED & BACKWARD-COMPATIBLE VERSION
    save_strategy="epoch",
    eval_strategy="epoch",                # ← this one works on both old and new transformers
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
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
    train_dataset=train_dataset, # <--- UPDATED
    eval_dataset=eval_dataset,   # <--- NEW
    data_collator=data_collator,
)

print("\n" + "="*60)
print("🚀 STARTING TRAINING")
print("="*60)
# Updated print statement to reflect the new train_dataset size
print(f"\nTotal steps per epoch: ~{len(train_dataset) // (BATCH_SIZE * GRAD_ACCUM_STEPS)}") 
print(f"Total steps: ~{len(train_dataset) * NUM_EPOCHS // (BATCH_SIZE * GRAD_ACCUM_STEPS)}")
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
# The trainer automatically loads the best model if load_best_model_at_end=True
model.save_pretrained(f"{OUTPUT_DIR}/final")
tokenizer.save_pretrained(f"{OUTPUT_DIR}/final")

print(f"\n🎉 Guardian training complete!")
print(f"\n📁 Model saved to: {OUTPUT_DIR}/final/")
print(f"📊 Logs saved to: {OUTPUT_DIR}/logs/")
print(f"\n🧪 Test with:")
print(f"  python test_guardian.py")