# Guardian LLM - RunPod Quick Start

## 1. Create Pod

- **Template**: RunPod PyTorch 2.4+ (or latest)
- **GPU**: A100 40GB (recommended) or A100 80GB
- **Disk**: 50GB+ (model downloads ~14GB)

## 2. Setup Environment

```bash
# SSH into pod, then:
cd /workspace

# Clone repo (or upload files)
git clone https://github.com/FirebirdSolutions/Guardian.git
cd Guardian

# Run setup script
bash runpod_setup.sh
```

## 3. Train

```bash
# Quick test (smaller model, fewer epochs)
python train_guardian_llm.py \
  --training-file "Fine Tuning/training-data-final.jsonl" \
  --model-size small \
  --epochs 5 \
  --output-dir ./guardian-test

# Full training (7B model, 20 epochs)
python train_guardian_llm.py \
  --training-file "Fine Tuning/training-data-final.jsonl" \
  --model-size large \
  --epochs 20 \
  --output-dir ./guardian-output
```

## 4. Monitor

```bash
# In another terminal
tensorboard --logdir ./guardian-output/logs --bind_all
# Access via RunPod's HTTP port (usually 6006)
```

## 5. Expected Times (A100 40GB)

| Model Size | Params | Time/Epoch | Total (20 epochs) |
|------------|--------|------------|-------------------|
| tiny | 500M | ~2 min | ~40 min |
| small | 1.5B | ~5 min | ~1.5 hr |
| medium | 3B | ~12 min | ~4 hr |
| large | 7B | ~25 min | ~8 hr |

## 6. Download Trained Model

```bash
# Zip the output
cd /workspace/Guardian
zip -r guardian-trained.zip guardian-output/final/

# Download via RunPod UI or:
# Use runpodctl or scp
```

## 7. Test Locally

```bash
# After downloading
python -m guardian_llm.cli \
  --model ./guardian-output/final \
  --interactive
```

## Troubleshooting

**Out of Memory**: Reduce batch size
```bash
python train_guardian_llm.py --batch-size 8 ...
```

**Slow Training**: Ensure Flash Attention installed
```bash
pip install flash-attn --no-build-isolation
```

**Model Not Learning**: Check loss is decreasing in TensorBoard
