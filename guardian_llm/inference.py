"""
Guardian LLM Inference Engine

Streaming inference with tool execution for real-time crisis detection.
Designed for low-latency responses in crisis situations.
"""

import re
import json
import time
import logging
from typing import Optional, Dict, Any, Generator, List, Callable
from dataclasses import dataclass
from queue import Queue
from threading import Thread
import torch

from .config import GuardianConfig, InferenceConfig
from .model import GuardianModel
from .tools import (
    GuardianTools,
    ToolCallParser,
    ToolExecutor,
    ToolResult,
    process_model_output_with_tools,
)
from .regions import Region, RegionManager

logger = logging.getLogger(__name__)


@dataclass
class GuardianResponse:
    """Complete response from Guardian inference."""
    # Core response
    output: str
    risk_level: str
    patterns_detected: List[str]

    # Tool interactions
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]

    # Resources (from tool calls)
    crisis_resources: List[Dict[str, Any]]

    # Metadata
    region: str
    inference_time_ms: float
    tokens_generated: int

    # Flags
    escalation_required: bool
    intervention_message: str


class StreamingCallback:
    """Callback for streaming token generation."""

    def __init__(self):
        self.tokens = []
        self.queue = Queue()
        self.done = False

    def on_token(self, token: str):
        """Called for each generated token."""
        self.tokens.append(token)
        self.queue.put(token)

    def on_done(self):
        """Called when generation is complete."""
        self.done = True
        self.queue.put(None)  # Sentinel

    def get_full_text(self) -> str:
        """Get full generated text."""
        return "".join(self.tokens)


class GuardianInference:
    """
    Main inference engine for Guardian LLM.

    Features:
    - Streaming token generation
    - Automatic tool execution
    - Multi-region support
    - Response parsing and validation
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        model: Optional[GuardianModel] = None,
        config: Optional[GuardianConfig] = None,
        inference_config: Optional[InferenceConfig] = None,
        default_region: Region = Region.NZ,
    ):
        """Initialize inference engine.

        Args:
            model_path: Path to trained model (loads if provided)
            model: Pre-loaded GuardianModel instance
            config: Model configuration
            inference_config: Inference configuration
            default_region: Default region for resources
        """
        self.config = config or GuardianConfig()
        self.inference_config = inference_config or InferenceConfig()
        self.default_region = default_region

        # Initialize tools
        self.tools = GuardianTools(default_region)
        self.tool_parser = ToolCallParser()
        self.tool_executor = ToolExecutor(self.tools)
        self.region_manager = RegionManager(default_region)

        # Load model
        if model is not None:
            self.model = model
        elif model_path is not None:
            self.model = GuardianModel.from_pretrained(model_path, config)
        else:
            self.model = GuardianModel(config)

        self._is_ready = False

    def load(self, model_path: str):
        """Load model from path.

        Args:
            model_path: Path to trained model
        """
        self.model = GuardianModel.from_pretrained(model_path, self.config)
        self._is_ready = True
        logger.info(f"Model loaded from {model_path}")

    def is_ready(self) -> bool:
        """Check if model is ready for inference."""
        return self._is_ready and self.model.is_loaded

    def generate(
        self,
        message: str,
        region: Optional[str] = None,
        system_prompt: Optional[str] = None,
        execute_tools: bool = True,
        stream: bool = False,
    ) -> GuardianResponse:
        """Generate response for a user message.

        Args:
            message: User's input message
            region: Region code (e.g., "NZ", "US")
            system_prompt: Custom system prompt
            execute_tools: Whether to execute tool calls
            stream: Whether to stream tokens (returns generator if True)

        Returns:
            GuardianResponse with full response data
        """
        start_time = time.time()

        # Determine region
        if region:
            try:
                region_enum = Region(region.upper())
            except ValueError:
                region_enum = self.default_region
        else:
            # Try to detect from message
            detected = self.region_manager.detect_region_from_message(message)
            region_enum = detected or self.default_region

        # Get region-specific system prompt if not provided
        if system_prompt is None:
            system_prompt = self.region_manager.get_system_prompt(region_enum)

        # Format prompt
        prompt = self.model.format_prompt(message, system_prompt, region_enum.value)

        # Generate
        if stream:
            # Return streaming generator
            return self._stream_generate(
                prompt, message, region_enum, execute_tools, start_time
            )
        else:
            return self._batch_generate(
                prompt, message, region_enum, execute_tools, start_time
            )

    def _batch_generate(
        self,
        prompt: str,
        original_message: str,
        region: Region,
        execute_tools: bool,
        start_time: float,
    ) -> GuardianResponse:
        """Generate response in batch mode.

        Args:
            prompt: Formatted prompt
            original_message: Original user message
            region: Detected region
            execute_tools: Whether to execute tools
            start_time: Start time for latency calculation

        Returns:
            GuardianResponse
        """
        # Tokenize
        inputs = self.model.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_seq_length,
        )

        device = self.model.get_device()
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate
        with torch.no_grad():
            outputs = self.model.model.generate(
                **inputs,
                max_new_tokens=self.inference_config.max_new_tokens,
                temperature=self.inference_config.temperature,
                top_p=self.inference_config.top_p,
                top_k=self.inference_config.top_k,
                repetition_penalty=self.inference_config.repetition_penalty,
                do_sample=self.inference_config.do_sample,
                num_beams=self.inference_config.num_beams,
                use_cache=self.inference_config.use_cache,
                pad_token_id=self.model.tokenizer.pad_token_id,
            )

        # Decode (only new tokens)
        generated = self.model.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True,
        )

        tokens_generated = outputs.shape[1] - inputs["input_ids"].shape[1]
        inference_time = (time.time() - start_time) * 1000

        return self._process_response(
            generated,
            original_message,
            region,
            execute_tools,
            inference_time,
            tokens_generated,
        )

    def _stream_generate(
        self,
        prompt: str,
        original_message: str,
        region: Region,
        execute_tools: bool,
        start_time: float,
    ) -> Generator[str, None, GuardianResponse]:
        """Generate response with streaming.

        Args:
            prompt: Formatted prompt
            original_message: Original user message
            region: Detected region
            execute_tools: Whether to execute tools
            start_time: Start time

        Yields:
            Generated tokens

        Returns:
            Final GuardianResponse
        """
        from transformers import TextIteratorStreamer

        # Tokenize
        inputs = self.model.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_seq_length,
        )

        device = self.model.get_device()
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Setup streamer
        streamer = TextIteratorStreamer(
            self.model.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        # Generate in thread
        generation_kwargs = {
            **inputs,
            "max_new_tokens": self.inference_config.max_new_tokens,
            "temperature": self.inference_config.temperature,
            "top_p": self.inference_config.top_p,
            "do_sample": self.inference_config.do_sample,
            "streamer": streamer,
            "pad_token_id": self.model.tokenizer.pad_token_id,
        }

        thread = Thread(target=self.model.model.generate, kwargs=generation_kwargs)
        thread.start()

        # Stream tokens
        generated_tokens = []
        for token in streamer:
            generated_tokens.append(token)
            yield token

        thread.join()

        # Process final response
        generated = "".join(generated_tokens)
        inference_time = (time.time() - start_time) * 1000

        return self._process_response(
            generated,
            original_message,
            region,
            execute_tools,
            inference_time,
            len(generated_tokens),
        )

    def _process_response(
        self,
        generated: str,
        original_message: str,
        region: Region,
        execute_tools: bool,
        inference_time_ms: float,
        tokens_generated: int,
    ) -> GuardianResponse:
        """Process generated text into structured response.

        Args:
            generated: Raw generated text
            original_message: Original user message
            region: User's region
            execute_tools: Whether to execute tools
            inference_time_ms: Inference time
            tokens_generated: Number of tokens

        Returns:
            Structured GuardianResponse
        """
        # Process with tools
        processed = process_model_output_with_tools(
            generated,
            self.tools,
            execute_tools=execute_tools,
        )

        # Extract risk level
        risk_level = self._extract_risk_level(generated)

        # Extract patterns
        patterns = self._extract_patterns(generated)

        # Get crisis resources from tool results
        crisis_resources = []
        for result in processed["tool_results"]:
            if result["success"] and result["data"]:
                data = result["data"]
                if "resources" in data:
                    crisis_resources.extend(data["resources"])

        # Determine if escalation required
        escalation_required = risk_level == "CRITICAL" or any(
            indicator in generated.lower()
            for indicator in ["escalate", "immediate", "emergency", "imminent"]
        )

        # Generate intervention message
        intervention_message = self._extract_intervention(generated)

        return GuardianResponse(
            output=processed["output"],
            risk_level=risk_level,
            patterns_detected=patterns,
            tool_calls=processed["tool_calls"],
            tool_results=processed["tool_results"],
            crisis_resources=crisis_resources,
            region=region.value,
            inference_time_ms=inference_time_ms,
            tokens_generated=tokens_generated,
            escalation_required=escalation_required,
            intervention_message=intervention_message,
        )

    def _extract_risk_level(self, output: str) -> str:
        """Extract risk level from output."""
        match = re.search(r'RISK LEVEL:\s*(\w+)', output, re.IGNORECASE)
        if match:
            level = match.group(1).upper()
            if level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                return level

        # Fallback
        for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if level in output.upper():
                return level

        return "MEDIUM"

    def _extract_patterns(self, output: str) -> List[str]:
        """Extract detected patterns from output."""
        patterns = []

        match = re.search(r'PATTERNS DETECTED:\s*(.+?)(?:\n|ACTION)', output, re.IGNORECASE | re.DOTALL)
        if match:
            pattern_text = match.group(1)
            # Split by comma or newline
            for p in re.split(r'[,\n]', pattern_text):
                p = p.strip().strip('•-')
                if p and len(p) > 2:
                    patterns.append(p)

        return patterns

    def _extract_intervention(self, output: str) -> str:
        """Extract intervention message from output."""
        # Look for INTERVENTION section
        match = re.search(r'INTERVENTION:?\s*(.+?)(?:ESCALATE|NOTE|SOURCE|$)', output, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback: look for resource list
        resources = re.findall(r'[•\-]\s*(\d+.*?)(?:\n|$)', output)
        if resources:
            return "Crisis resources:\n" + "\n".join(f"• {r}" for r in resources)

        return ""

    def detect_crisis(self, message: str, region: str = "NZ") -> Dict[str, Any]:
        """Quick crisis detection without full response generation.

        Args:
            message: User message to check
            region: Region code

        Returns:
            Dict with crisis detection results
        """
        response = self.generate(message, region=region, execute_tools=False)

        return {
            "is_crisis": response.risk_level in ["CRITICAL", "HIGH"],
            "risk_level": response.risk_level,
            "patterns": response.patterns_detected,
            "escalation_required": response.escalation_required,
            "inference_time_ms": response.inference_time_ms,
        }

    def get_resources_for_situation(
        self,
        situation_type: str,
        region: str = "NZ",
    ) -> List[Dict[str, Any]]:
        """Get crisis resources for a situation type.

        Args:
            situation_type: Type of crisis
            region: Region code

        Returns:
            List of crisis resources
        """
        result = self.tools._get_crisis_resources(region, situation_type)
        if result.success:
            return result.data.get("resources", [])
        return []


class GuardianPipeline:
    """
    High-level pipeline for Guardian inference.

    Provides a simple interface for common use cases.
    """

    def __init__(
        self,
        model_path: str,
        default_region: str = "NZ",
    ):
        """Initialize pipeline.

        Args:
            model_path: Path to trained model
            default_region: Default region
        """
        self.inference = GuardianInference(
            model_path=model_path,
            default_region=Region(default_region),
        )

    def __call__(
        self,
        message: str,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a message through the pipeline.

        Args:
            message: User message
            region: Optional region override

        Returns:
            Dict with response data
        """
        response = self.inference.generate(message, region=region)

        return {
            "risk_level": response.risk_level,
            "output": response.output,
            "resources": response.crisis_resources,
            "escalation_required": response.escalation_required,
            "intervention": response.intervention_message,
            "inference_time_ms": response.inference_time_ms,
        }

    def is_crisis(self, message: str, region: str = "NZ") -> bool:
        """Check if message indicates a crisis.

        Args:
            message: User message
            region: Region code

        Returns:
            True if crisis detected
        """
        result = self.inference.detect_crisis(message, region)
        return result["is_crisis"]

    def get_resources(
        self,
        situation: str = "mental_health",
        region: str = "NZ",
    ) -> List[Dict]:
        """Get crisis resources.

        Args:
            situation: Situation type
            region: Region code

        Returns:
            List of resources
        """
        return self.inference.get_resources_for_situation(situation, region)


def create_inference_engine(
    model_path: str,
    region: str = "NZ",
    **kwargs,
) -> GuardianInference:
    """Factory function to create inference engine.

    Args:
        model_path: Path to trained model
        region: Default region
        **kwargs: Additional configuration

    Returns:
        Configured GuardianInference instance
    """
    config = GuardianConfig()
    inference_config = InferenceConfig(**kwargs)

    engine = GuardianInference(
        model_path=model_path,
        config=config,
        inference_config=inference_config,
        default_region=Region(region),
    )

    return engine
