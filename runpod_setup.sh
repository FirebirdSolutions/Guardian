#!/bin/bash
# =============================================================================
# Guardian LLM - RunPod Setup Script
# =============================================================================
# For RunPod PyTorch 2.x template (tested on 2.4+)
#
# Usage:
#   1. Create RunPod pod with PyTorch template (A100 40GB recommended)
#   2. Upload this script + training data to /workspace/
#   3. Run: bash runpod_setup.sh
#   4. Train: python train_guardian_llm.py --training-file training-data-normalized.jsonl
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "Guardian LLM - RunPod Environment Setup"
echo "=============================================="

# -----------------------------------------------------------------------------
# 1. System Dependencies
# -----------------------------------------------------------------------------
echo ""
echo "[1/5] Installing system dependencies..."
apt-get update -qq && apt-get install -y -qq git-lfs > /dev/null 2>&1 || true

# -----------------------------------------------------------------------------
# 2. Python Dependencies
# -----------------------------------------------------------------------------
echo "[2/5] Installing Python packages..."

# Core training packages
pip install -q --upgrade pip

pip install -q \
    torch \
    transformers>=4.40.0 \
    datasets>=2.18.0 \
    peft>=0.10.0 \
    bitsandbytes>=0.43.0 \
    accelerate>=0.28.0 \
    tensorboard \
    safetensors \
    sentencepiece \
    protobuf

# For faster downloads
pip install -q hf_transfer
export HF_HUB_ENABLE_HF_TRANSFER=1

# Optional: Flash Attention 2 (significant speedup on A100/H100)
echo "[2/5] Installing Flash Attention 2 (this may take a few minutes)..."
pip install -q flash-attn --no-build-isolation 2>/dev/null || echo "Flash Attention install failed - will use default attention"

# -----------------------------------------------------------------------------
# 3. Verify GPU
# -----------------------------------------------------------------------------
echo "[3/5] Checking GPU..."
python3 << 'EOF'
import torch
print(f"  PyTorch version: {torch.__version__}")
print(f"  CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print(f"  CUDA version: {torch.version.cuda}")
else:
    print("  WARNING: No GPU detected!")
EOF

# -----------------------------------------------------------------------------
# 4. Verify Packages
# -----------------------------------------------------------------------------
echo "[4/5] Verifying packages..."
python3 << 'EOF'
import transformers
import peft
import bitsandbytes
import datasets
print(f"  transformers: {transformers.__version__}")
print(f"  peft: {peft.__version__}")
print(f"  bitsandbytes: {bitsandbytes.__version__}")
print(f"  datasets: {datasets.__version__}")

# Check flash attention
try:
    from flash_attn import flash_attn_func
    print("  flash-attn: installed ✓")
except ImportError:
    print("  flash-attn: not installed (will use default attention)")
EOF

# -----------------------------------------------------------------------------
# 5. Create workspace structure
# -----------------------------------------------------------------------------
echo "[5/5] Setting up workspace..."
cd /workspace

# Create directories if not exist
mkdir -p guardian-output logs

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Upload your training data:"
echo "   - training-data-normalized.jsonl"
echo "   - train_guardian_llm.py"
echo "   - guardian_llm/ folder"
echo ""
echo "2. Start training:"
echo "   python train_guardian_llm.py \\"
echo "     --training-file training-data-normalized.jsonl \\"
echo "     --output-dir ./guardian-output \\"
echo "     --model-size large \\"
echo "     --epochs 20"
echo ""
echo "3. Monitor with TensorBoard:"
echo "   tensorboard --logdir ./guardian-output/logs --bind_all"
echo ""
echo "=============================================="
