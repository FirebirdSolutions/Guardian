"""
Guardian LLM Export Utilities

Export trained models to various formats for deployment:
- GGUF for llama.cpp / Ollama
- ONNX for cross-platform deployment
- SafeTensors for HuggingFace
"""

import os
import json
import shutil
import subprocess
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass

import torch

from .config import GuardianConfig, ExportConfig
from .model import GuardianModel

logger = logging.getLogger(__name__)


@dataclass
class ExportResult:
    """Result of model export operation."""
    success: bool
    format: str
    output_path: str
    file_size_mb: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class GuardianExporter:
    """Export Guardian models to various formats."""

    GGUF_QUANTIZATIONS = {
        "q4_k_m": "Best balance of size and quality",
        "q4_k_s": "Smaller, slightly lower quality",
        "q5_k_m": "Higher quality, larger size",
        "q5_k_s": "Good balance for Q5",
        "q8_0": "High quality, 8-bit",
        "f16": "Full float16, largest",
        "f32": "Full float32, maximum quality",
    }

    def __init__(
        self,
        model_path: str,
        config: Optional[ExportConfig] = None,
    ):
        """Initialize exporter.

        Args:
            model_path: Path to trained model
            config: Export configuration
        """
        self.model_path = Path(model_path)
        self.config = config or ExportConfig()

        # Verify model exists
        if not self.model_path.exists():
            raise ValueError(f"Model path does not exist: {model_path}")

    def export_all(self) -> Dict[str, ExportResult]:
        """Export to all configured formats.

        Returns:
            Dict mapping format name to export result
        """
        results = {}

        # Merge LoRA if needed
        merged_path = self._ensure_merged_model()

        if self.config.export_safetensors:
            results["safetensors"] = self.export_safetensors(merged_path)

        if self.config.export_gguf:
            results["gguf"] = self.export_gguf(
                merged_path,
                quantization=self.config.gguf_quantization,
            )

        if self.config.export_onnx:
            results["onnx"] = self.export_onnx(merged_path)

        return results

    def _ensure_merged_model(self) -> Path:
        """Ensure we have a merged (non-LoRA) model.

        Returns:
            Path to merged model
        """
        adapter_config = self.model_path / "adapter_config.json"

        if adapter_config.exists() and self.config.merge_lora:
            # Need to merge LoRA weights
            logger.info("Merging LoRA weights into base model...")
            merged_path = Path(self.config.export_dir) / "merged"
            merged_path.mkdir(parents=True, exist_ok=True)

            # Load and merge
            model = GuardianModel.from_pretrained(str(self.model_path))
            model.merge_and_unload()
            model.save(str(merged_path))

            return merged_path
        else:
            return self.model_path

    def export_safetensors(
        self,
        model_path: Optional[Path] = None,
    ) -> ExportResult:
        """Export model to SafeTensors format.

        Args:
            model_path: Path to model (uses self.model_path if None)

        Returns:
            ExportResult
        """
        model_path = model_path or self.model_path
        output_dir = Path(self.config.export_dir) / "safetensors"
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Load model
            model = GuardianModel.from_pretrained(str(model_path))

            # Save with safetensors
            model.model.save_pretrained(
                str(output_dir),
                safe_serialization=True,
            )
            model.tokenizer.save_pretrained(str(output_dir))

            # Copy config files
            for config_file in ["guardian_config.json", "config.json"]:
                src = model_path / config_file
                if src.exists():
                    shutil.copy(src, output_dir / config_file)

            # Calculate size
            total_size = sum(
                f.stat().st_size for f in output_dir.rglob("*.safetensors")
            )
            size_mb = total_size / (1024 * 1024)

            logger.info(f"SafeTensors export complete: {output_dir} ({size_mb:.1f}MB)")

            return ExportResult(
                success=True,
                format="safetensors",
                output_path=str(output_dir),
                file_size_mb=size_mb,
            )

        except Exception as e:
            logger.error(f"SafeTensors export failed: {e}")
            return ExportResult(
                success=False,
                format="safetensors",
                output_path="",
                file_size_mb=0,
                error=str(e),
            )

    def export_gguf(
        self,
        model_path: Optional[Path] = None,
        quantization: str = "q4_k_m",
    ) -> ExportResult:
        """Export model to GGUF format for llama.cpp.

        Args:
            model_path: Path to model
            quantization: Quantization type

        Returns:
            ExportResult
        """
        model_path = model_path or self.model_path
        output_dir = Path(self.config.export_dir) / "gguf"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"guardian-{quantization}.gguf"

        try:
            # Check if llama.cpp convert script is available
            convert_script = self._find_llama_cpp_convert()

            if convert_script:
                # Use llama.cpp conversion
                result = self._convert_with_llama_cpp(
                    model_path,
                    output_file,
                    quantization,
                    convert_script,
                )
            else:
                # Provide instructions
                result = self._gguf_conversion_instructions(
                    model_path,
                    output_file,
                    quantization,
                )

            return result

        except Exception as e:
            logger.error(f"GGUF export failed: {e}")
            return ExportResult(
                success=False,
                format="gguf",
                output_path="",
                file_size_mb=0,
                error=str(e),
            )

    def _find_llama_cpp_convert(self) -> Optional[Path]:
        """Find llama.cpp convert script."""
        possible_paths = [
            Path.home() / "llama.cpp" / "convert.py",
            Path("/opt/llama.cpp/convert.py"),
            Path("./llama.cpp/convert.py"),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # Try to find via which
        try:
            result = subprocess.run(
                ["which", "llama-cpp-convert"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass

        return None

    def _convert_with_llama_cpp(
        self,
        model_path: Path,
        output_file: Path,
        quantization: str,
        convert_script: Path,
    ) -> ExportResult:
        """Convert using llama.cpp tools."""
        # First convert to f16 GGUF
        f16_file = output_file.parent / "guardian-f16.gguf"

        convert_cmd = [
            "python", str(convert_script),
            str(model_path),
            "--outfile", str(f16_file),
            "--outtype", "f16",
        ]

        logger.info(f"Running: {' '.join(convert_cmd)}")
        result = subprocess.run(convert_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return ExportResult(
                success=False,
                format="gguf",
                output_path="",
                file_size_mb=0,
                error=f"Conversion failed: {result.stderr}",
            )

        # Then quantize if needed
        if quantization != "f16":
            quantize_cmd = [
                "llama-quantize",
                str(f16_file),
                str(output_file),
                quantization.upper(),
            ]

            logger.info(f"Running: {' '.join(quantize_cmd)}")
            result = subprocess.run(quantize_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                # Fall back to f16
                shutil.move(str(f16_file), str(output_file))
                logger.warning(f"Quantization failed, using f16: {result.stderr}")

            # Clean up f16 file
            if f16_file.exists() and output_file.exists():
                f16_file.unlink()
        else:
            shutil.move(str(f16_file), str(output_file))

        size_mb = output_file.stat().st_size / (1024 * 1024)

        return ExportResult(
            success=True,
            format="gguf",
            output_path=str(output_file),
            file_size_mb=size_mb,
            metadata={"quantization": quantization},
        )

    def _gguf_conversion_instructions(
        self,
        model_path: Path,
        output_file: Path,
        quantization: str,
    ) -> ExportResult:
        """Generate instructions for manual GGUF conversion."""
        instructions = f"""
GGUF Export Instructions
========================

llama.cpp convert script not found. To export to GGUF format:

1. Clone llama.cpp:
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make

2. Convert the model:
   python convert.py {model_path} --outfile {output_file.parent}/guardian-f16.gguf --outtype f16

3. Quantize (optional but recommended):
   ./quantize {output_file.parent}/guardian-f16.gguf {output_file} {quantization.upper()}

Model path: {model_path}
Output path: {output_file}
Quantization: {quantization}
"""

        # Save instructions
        instructions_file = output_file.parent / "gguf_export_instructions.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(instructions_file, 'w') as f:
            f.write(instructions)

        logger.info(f"GGUF conversion instructions saved to {instructions_file}")

        return ExportResult(
            success=False,
            format="gguf",
            output_path=str(instructions_file),
            file_size_mb=0,
            error="llama.cpp not found - see instructions file",
            metadata={"instructions_file": str(instructions_file)},
        )

    def export_onnx(
        self,
        model_path: Optional[Path] = None,
    ) -> ExportResult:
        """Export model to ONNX format.

        Args:
            model_path: Path to model

        Returns:
            ExportResult
        """
        model_path = model_path or self.model_path
        output_dir = Path(self.config.export_dir) / "onnx"
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            from optimum.onnxruntime import ORTModelForCausalLM

            logger.info("Exporting to ONNX...")

            # Export using optimum
            ort_model = ORTModelForCausalLM.from_pretrained(
                str(model_path),
                export=True,
            )
            ort_model.save_pretrained(str(output_dir))

            # Also save tokenizer
            model = GuardianModel.from_pretrained(str(model_path))
            model.tokenizer.save_pretrained(str(output_dir))

            # Calculate size
            total_size = sum(
                f.stat().st_size for f in output_dir.rglob("*.onnx")
            )
            size_mb = total_size / (1024 * 1024)

            logger.info(f"ONNX export complete: {output_dir} ({size_mb:.1f}MB)")

            return ExportResult(
                success=True,
                format="onnx",
                output_path=str(output_dir),
                file_size_mb=size_mb,
            )

        except ImportError:
            error_msg = "optimum library required for ONNX export. Install with: pip install optimum[onnxruntime]"
            logger.error(error_msg)
            return ExportResult(
                success=False,
                format="onnx",
                output_path="",
                file_size_mb=0,
                error=error_msg,
            )
        except Exception as e:
            logger.error(f"ONNX export failed: {e}")
            return ExportResult(
                success=False,
                format="onnx",
                output_path="",
                file_size_mb=0,
                error=str(e),
            )

    def create_ollama_modelfile(
        self,
        gguf_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Create an Ollama Modelfile for the exported GGUF.

        Args:
            gguf_path: Path to GGUF file
            output_path: Where to save Modelfile

        Returns:
            Modelfile content
        """
        modelfile = f"""# Guardian Crisis Detection Model
# Specialized for NZ mental health crisis detection

FROM {gguf_path}

# Low temperature for consistent crisis response
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 50
PARAMETER repeat_penalty 1.1

# System prompt
SYSTEM \"\"\"You are Guardian, an AI safety system for crisis detection.

VERIFIED NZ CRISIS RESOURCES:
• 111 - Emergency services
• 1737 - Mental health crisis (Free 24/7 call or text)
• 0800 543 354 - Lifeline NZ (Free 24/7)
• 0800 456 450 - Family Violence Hotline (Free 24/7)
• 0800 733 843 - Women's Refuge (Free 24/7)

Your role is to:
1. Detect crisis indicators in user messages
2. Provide verified NZ crisis resources
3. Never hallucinate phone numbers
4. Escalate critical situations appropriately
\"\"\"

# Template for chat
TEMPLATE \"\"\"{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
{{{{ end }}}}<|im_start|>assistant
{{{{ .Response }}}}<|im_end|>
\"\"\"

# Stop tokens
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|im_start|>"

# License
LICENSE \"\"\"
Guardian Crisis Detection Model
Open source under MIT License
For crisis detection and mental health safety
\"\"\"
"""

        if output_path:
            with open(output_path, 'w') as f:
                f.write(modelfile)
            logger.info(f"Modelfile saved to {output_path}")

        return modelfile

    def export_for_ollama(self) -> Dict[str, Any]:
        """Complete export pipeline for Ollama deployment.

        Returns:
            Dict with export paths and instructions
        """
        results = {}

        # Export GGUF
        merged_path = self._ensure_merged_model()
        gguf_result = self.export_gguf(merged_path)
        results["gguf"] = gguf_result

        if gguf_result.success:
            # Create Modelfile
            modelfile_path = Path(self.config.export_dir) / "Modelfile"
            self.create_ollama_modelfile(
                gguf_result.output_path,
                str(modelfile_path),
            )
            results["modelfile"] = str(modelfile_path)

            # Instructions
            results["instructions"] = f"""
Ollama Deployment Instructions
==============================

1. Create the model in Ollama:
   cd {self.config.export_dir}
   ollama create guardian -f Modelfile

2. Run the model:
   ollama run guardian

3. Test with a message:
   ollama run guardian "I'm feeling really hopeless today"

Files created:
- GGUF model: {gguf_result.output_path}
- Modelfile: {modelfile_path}
"""

        return results


def export_model(
    model_path: str,
    output_dir: str = "./guardian-export",
    formats: List[str] = None,
    gguf_quantization: str = "q4_k_m",
) -> Dict[str, ExportResult]:
    """Convenience function to export a model.

    Args:
        model_path: Path to trained model
        output_dir: Output directory
        formats: List of formats to export (safetensors, gguf, onnx)
        gguf_quantization: GGUF quantization type

    Returns:
        Dict of export results
    """
    if formats is None:
        formats = ["safetensors", "gguf"]

    config = ExportConfig(
        export_dir=output_dir,
        export_safetensors="safetensors" in formats,
        export_gguf="gguf" in formats,
        export_onnx="onnx" in formats,
        gguf_quantization=gguf_quantization,
    )

    exporter = GuardianExporter(model_path, config)
    return exporter.export_all()
