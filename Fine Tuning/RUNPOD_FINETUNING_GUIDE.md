# Fine-Tuning on RunPod: The Fucktard's Guide

## What You're About To Do

You're going to:

1. Rent a beefy GPU on RunPod
2. Upload your training data
3. Run a fine-tuning script
4. Wait several hours while it trains
5. Download your fine-tuned model
6. Use it locally or deploy it

**Cost estimate:** $5-30 depending on GPU and training time (probably 4-8 hours)

---

## pip install transformers peft datasets hf_transfer bitsandbytes tensorboard



## Part 1: Choose Your Base Model

Before RunPod, decide what you're fine-tuning:

### Recommended Models (December 2024)

**For Kiwi Echo (your use case):**

1. **Qwen2.5-7B-Instruct** ⭐ RECOMMENDED
   
   - Size: 7B parameters (~14GB)
   - Quality: Excellent instruction following
   - Speed: Fast inference
   - Vibe: Smart but not overbearing
   - HuggingFace: `Qwen/Qwen2.5-7B-Instruct`

2. **Mistral-7B-Instruct-v0.3**
   
   - Size: 7B parameters
   - Quality: Great at coding
   - Speed: Very fast
   - Vibe: Direct and helpful
   - HuggingFace: `mistralai/Mistral-7B-Instruct-v0.3`

3. **Llama-3.2-8B-Instruct**
   
   - Size: 8B parameters
   - Quality: Solid all-rounder
   - Speed: Fast
   - Vibe: Balanced
   - HuggingFace: `meta-llama/Llama-3.2-8B-Instruct`

**My pick for you:** Qwen2.5-7B-Instruct

- Already good at code
- Handles multi-turn well
- Won't be overbearing with safety nannying
- Fast enough to run locally later

---

## Part 2: Prepare Your Data

### Convert to Alpaca Format

```bash
python convert_for_finetuning.py final_training.jsonl alpaca_training.jsonl alpaca
```

This creates:

```json
{"instruction": "Create a C# extension method...", "input": "", "output": "using System..."}
```

### Split Train/Validation (Optional but Recommended)

```bash
# Split 95% train, 5% validation
head -n 3360 alpaca_training.jsonl > train.jsonl
tail -n 177 alpaca_training.jsonl > validation.jsonl
```

---

## Part 3: Set Up RunPod

### 1. Create Account

- Go to https://runpod.io
- Sign up (use Google or email)
- Add credits ($20-50 to start)

### 2. Choose GPU

**GPU Options (pick based on budget/speed):**

| GPU       | VRAM | Speed     | Cost/hr | Best For        |
| --------- | ---- | --------- | ------- | --------------- |
| RTX 4090  | 24GB | Fast      | ~$0.50  | Good balance    |
| RTX A6000 | 48GB | Medium    | ~$0.80  | Bigger batches  |
| A100 40GB | 40GB | Very Fast | ~$1.50  | $$ but quick    |
| A100 80GB | 80GB | Very Fast | ~$2.50  | Overkill for 7B |

**For 7B model fine-tuning:** RTX 4090 is perfect (24GB is plenty)

### 3. Deploy Pod

1. Click **"Deploy"** in RunPod dashboard
2. Choose **GPU Type**: RTX 4090
3. Choose **Template**: 
   - Search for "pytorch" or "runpod/pytorch"
   - OR use "RunPod Pytorch" template
4. **Container Disk**: 50GB minimum
5. **Volume**: Optional (for saving model), 50GB recommended
6. Click **"Deploy"**

Wait 1-2 minutes for pod to start.

### 4. Connect to Pod

Two options:

**Option A: JupyterLab** (easier)

- Click "Connect" → "Start Jupyter Lab"
- Opens in browser
- Use terminal + notebook

**Option B: SSH** (for pros)

- Click "Connect" → "TCP Port Mappings"
- Copy SSH command
- Connect from your terminal

---

## Part 4: Upload Your Data

### In JupyterLab:

1. Click upload button (top left)
2. Upload `train.jsonl` and `validation.jsonl`

### Or via terminal:

```bash
# On your local machine (in new terminal)
scp -P [PORT] train.jsonl root@[RUNPOD-IP]:/workspace/
scp -P [PORT] validation.jsonl root@[RUNPOD-IP]:/workspace/
```

(Get PORT and IP from RunPod "Connect" dropdown)

---

## Part 5: Fine-Tuning Script

I'll give you two options: **Easy (Axolotl)** or **Manual (Transformers)**

### Option A: Easy Mode with Axolotl ⭐ RECOMMENDED

Axolotl is a fine-tuning framework that handles everything.

**In your RunPod terminal:**

```bash
# Install Axolotl
cd /workspace
git clone https://github.com/OpenAccess-AI-Collective/axolotl
cd axolotl
pip install -e '.[flash-attn,deepspeed]'

# This takes 5-10 minutes, grab a coffee
```

**Create config file:**

```bash
cat > qwen_echo_config.yml << 'EOF'
base_model: Qwen/Qwen2.5-7B-Instruct
model_type: AutoModelForCausalLM
tokenizer_type: AutoTokenizer

load_in_8bit: false
load_in_4bit: true  # Use 4-bit for 24GB GPU
strict: false

datasets:
  - path: train.jsonl
    type: alpaca
val_set_size: 0.05  # Or specify validation.jsonl path

output_dir: ./qwen-echo-output

# Training hyperparameters
sequence_len: 2048  # Max length (your data is long, so use 2048+)
sample_packing: true
pad_to_sequence_len: true

adapter: qlora  # Use QLoRA (efficient)
lora_r: 32
lora_alpha: 16
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - v_proj
  - k_proj
  - o_proj
  - gate_proj
  - down_proj
  - up_proj

# LoRA layers to train
lora_target_linear: true

# Training params
gradient_accumulation_steps: 4
micro_batch_size: 1  # Adjust based on GPU memory
num_epochs: 3
optimizer: adamw_bnb_8bit
lr_scheduler: cosine
learning_rate: 0.0002

# Logging
logging_steps: 10
save_steps: 100
eval_steps: 100

# Speedups
bf16: true
tf32: true
gradient_checkpointing: true
flash_attention: true

# Weights & Biases (optional, for tracking)
wandb_project: echo-finetuning
wandb_run_id: qwen-echo-v1
EOF
```

**Run the fine-tuning:**

```bash
accelerate launch -m axolotl.cli.train qwen_echo_config.yml
```

**Time estimate:** 4-8 hours on RTX 4090

**What happens:**

- Loads Qwen2.5-7B model
- Trains LoRA adapters on your data
- Saves checkpoints every 100 steps
- Creates final model in `qwen-echo-output/`

### Option B: Manual with Transformers (More Control)

If Axolotl fails or you want more control:

```bash
# Install dependencies
pip install transformers datasets peft bitsandbytes accelerate
```

**Create training script:**

```python
# save as train.py
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch

# Load model and tokenizer
model_name = "Qwen/Qwen2.5-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Prepare for LoRA
model = prepare_model_for_kbit_training(model)

# LoRA config
lora_config = LoraConfig(
    r=32,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Load dataset
dataset = load_dataset('json', data_files={
    'train': 'train.jsonl',
    'validation': 'validation.jsonl'
})

# Tokenize
def tokenize_function(examples):
    prompts = [f"### Instruction:\n{inst}\n\n### Response:\n{out}" 
               for inst, out in zip(examples['instruction'], examples['output'])]
    return tokenizer(prompts, truncation=True, max_length=2048, padding="max_length")

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset['train'].column_names)

# Training arguments
training_args = TrainingArguments(
    output_dir="./qwen-echo-output",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    bf16=True,
    save_steps=100,
    logging_steps=10,
    evaluation_strategy="steps",
    eval_steps=100,
    save_total_limit=3,
    load_best_model_at_end=True,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    eval_dataset=tokenized_dataset['validation'],
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# Train
trainer.train()

# Save
model.save_pretrained("./qwen-echo-final")
tokenizer.save_pretrained("./qwen-echo-final")
```

**Run it:**

```bash
python train.py
```

---

## Part 6: Monitor Training

### Check Progress

```bash
# Watch logs
tail -f qwen-echo-output/training_logs.txt

# Or if using wandb
# Go to https://wandb.ai and check your run
```

### What to Watch For

**Good signs:**

- Loss decreasing steadily
- Validation loss following train loss (not diverging)
- No OOM (Out of Memory) errors

**Bad signs:**

- Loss stuck or increasing
- Validation loss >> train loss (overfitting)
- GPU utilization < 80% (batch size too small)

### Troubleshooting

**Out of Memory:**

```yaml
# In config, reduce:
micro_batch_size: 1  # Already minimum
sequence_len: 1024   # Cut in half
lora_r: 16           # Reduce LoRA rank
```

**Too Slow:**

```yaml
# In config, increase:
micro_batch_size: 2
gradient_accumulation_steps: 2  # Reduce
```

---

## Part 7: Download Your Model

### After training completes:

**Option A: Download via JupyterLab**

1. Navigate to `qwen-echo-output/` folder
2. Right-click → Download
3. Downloads as zip

**Option B: Download via SCP**

```bash
# On your local machine
scp -r -P [PORT] root@[RUNPOD-IP]:/workspace/qwen-echo-output ./my-echo-model/
```

### What you get:

```
qwen-echo-output/
├── adapter_config.json      # LoRA config
├── adapter_model.bin         # LoRA weights (small! ~100-500MB)
├── tokenizer.json
├── tokenizer_config.json
└── special_tokens_map.json
```

**Important:** You need BOTH:

1. Original base model (Qwen2.5-7B-Instruct)
2. Your LoRA adapter files

---

## Part 8: Test Your Model Locally

### Install dependencies:

```bash
pip install transformers torch peft accelerate
```

### Load and test:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load base model
base_model = "Qwen/Qwen2.5-7B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(base_model)

# Load your LoRA adapter
model = PeftModel.from_pretrained(model, "./qwen-echo-output")

# Test it
prompt = "Create a C# extension method to convert strings to title case"
messages = [{"role": "user", "content": prompt}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)

outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7, do_sample=True)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(response)
```

### Expected output:

```
using System.Globalization;

public static class StringExtensions
{
    public static string ToTitleCase(this string input)
    {
        return CultureInfo.CurrentCulture.TextInfo.ToTitleCase(input);
    }
}
```

Plus possibly some swearing if it learned your style 😂

---

## Part 9: Deploy (Optional)

### Option A: Run Locally with Ollama

```bash
# Install Ollama (if not already)
curl https://ollama.ai/install.sh | sh

# Convert to GGUF format (for Ollama)
# Use llama.cpp converter
python convert-to-gguf.py ./qwen-echo-output

# Create Modelfile
cat > Modelfile << 'EOF'
FROM ./qwen-echo.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.9
SYSTEM You are Echo, a helpful Kiwi AI. You're direct, occasionally sweary about tech problems, and say "noice" when things work.
EOF

# Import to Ollama
ollama create echo -f Modelfile

# Run it
ollama run echo
```

### Option B: Deploy on RunPod Serverless

1. Create Docker image with your model
2. Push to Docker Hub
3. Deploy on RunPod Serverless
4. Get API endpoint

(This is its own guide - let me know if you want details)

### Option C: Host on your own server

- Use vLLM or TGI (Text Generation Inference)
- Expose via API
- Hook up to aiMate.nz

---

## Costs Breakdown

### One-time costs:

- **GPU rental:** $5-15 (4-8 hours on RTX 4090)
- **Storage:** Free (if you download immediately)
- **Total:** ~$10-20 for first fine-tune

### Ongoing costs (if deploying):

- **Local:** Free (runs on your hardware)
- **RunPod Serverless:** $0.0002-0.0005 per second of inference
- **Your own server:** Server costs

---

## Troubleshooting Common Fuckups

### "CUDA out of memory"

**Fix:** Reduce batch size, sequence length, or use 4-bit quantization

### "Model not learning" (loss not decreasing)

**Fix:** Check learning rate (try 1e-4 to 5e-4), increase epochs, check data quality

### "Model overfitting" (validation loss increasing)

**Fix:** Reduce epochs, add dropout, get more data

### "Takes forever to train"

**Fix:** Use bigger GPU, increase batch size, use flash attention

### "Model output is gibberish"

**Fix:** Probably tokenizer issue - make sure you're using the right chat template

### "Download is huge"

**Fix:** You're downloading the full model, not just LoRA adapters. LoRA files should be <1GB.

---

## Quick Command Reference

```bash
# Convert data
python convert_for_finetuning.py final_training.jsonl train.jsonl alpaca

# Split data
head -n 3360 train.jsonl > training.jsonl
tail -n 177 train.jsonl > validation.jsonl

# Run Axolotl
accelerate launch -m axolotl.cli.train config.yml

# Monitor
tail -f qwen-echo-output/training_logs.txt

# Download
scp -r -P PORT root@IP:/workspace/qwen-echo-output ./

# Test locally
python test_model.py
```

---

## Final Checklist

Before you start:

- [ ] Data converted to correct format
- [ ] RunPod account with credits
- [ ] GPU selected (RTX 4090 recommended)
- [ ] Base model chosen (Qwen2.5-7B-Instruct)
- [ ] Config file created
- [ ] Coffee made ☕

After training:

- [ ] Loss decreased significantly
- [ ] Model downloaded
- [ ] Tested locally
- [ ] Doesn't tell people to keep their legs shut 😅
- [ ] Actually sounds like you

---

## Need Help?

**If shit goes wrong:**

1. Check RunPod logs first
2. Google the error (seriously, most are common)
3. Ask in RunPod Discord
4. Come back here and I'll help debug

**Common resources:**

- Axolotl docs: https://github.com/OpenAccess-AI-Collective/axolotl
- RunPod docs: https://docs.runpod.io
- Transformers docs: https://huggingface.co/docs/transformers

---

## Expected Timeline

- **Setup:** 30 minutes
- **Training:** 4-8 hours (let it run overnight)
- **Download:** 10-30 minutes
- **Testing:** 15 minutes
- **Tweaking:** Forever (welcome to ML)

**Total:** One evening to start, one morning to finish

---

You're now equipped to fine-tune your sweary Kiwi AI. 

FFS, go make Echo real! 🇳🇿🚀
