"""
Guardian LLM Tool System

Defines tools that the Guardian model can call to dynamically fetch
crisis resources, log incidents, and validate information.

The model generates tool calls in the format:
[TOOL_CALL: function_name(param1='value1', param2='value2')]

These are parsed and executed by the inference engine.
"""

import re
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .regions import Region, RegionManager, CrisisResource

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Represents a parsed tool call from model output."""
    name: str
    arguments: Dict[str, Any]
    raw_text: str = ""


@dataclass
class ToolResult:
    """Result of executing a tool call."""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class Tool:
    """Definition of a tool that Guardian can call."""
    name: str
    description: str
    parameters: Dict[str, Dict[str, Any]]  # param_name -> {type, description, required}
    handler: Callable[..., ToolResult]


class GuardianTools:
    """
    Tool system for Guardian LLM.

    Provides tools for:
    - get_crisis_resources: Fetch verified crisis resources for a region
    - log_incident: Log a crisis incident for monitoring
    - check_hallucination: Verify if a resource is fake/wrong region
    - get_regional_context: Get cultural/linguistic context for a region
    """

    def __init__(self, default_region: Region = Region.NZ):
        """Initialize tool system.

        Args:
            default_region: Default region for resource lookups
        """
        self.region_manager = RegionManager(default_region)
        self.default_region = default_region
        self.incident_log: List[Dict] = []
        self.tools = self._register_tools()

    def _register_tools(self) -> Dict[str, Tool]:
        """Register all available tools."""
        return {
            "get_crisis_resources": Tool(
                name="get_crisis_resources",
                description="Fetch verified crisis resources for a region and situation type",
                parameters={
                    "region": {
                        "type": "string",
                        "description": "Region code (NZ, AU, US, UK, CA, IE)",
                        "required": False,
                        "default": "NZ",
                    },
                    "situation_type": {
                        "type": "string",
                        "description": "Type of crisis (mental_health, domestic_violence, suicide, youth, substance_abuse)",
                        "required": False,
                        "default": "mental_health",
                    },
                },
                handler=self._get_crisis_resources,
            ),
            "log_incident": Tool(
                name="log_incident",
                description="Log a crisis incident for monitoring and analysis",
                parameters={
                    "incident_data": {
                        "type": "object",
                        "description": "Incident details including type, severity, region",
                        "required": True,
                    },
                },
                handler=self._log_incident,
            ),
            "check_hallucination": Tool(
                name="check_hallucination",
                description="Check if a phone number is fake or from wrong region",
                parameters={
                    "number": {
                        "type": "string",
                        "description": "Phone number to verify",
                        "required": True,
                    },
                    "region": {
                        "type": "string",
                        "description": "Expected region for the number",
                        "required": False,
                        "default": "NZ",
                    },
                },
                handler=self._check_hallucination,
            ),
            "get_regional_context": Tool(
                name="get_regional_context",
                description="Get cultural and linguistic context for a region",
                parameters={
                    "region": {
                        "type": "string",
                        "description": "Region code",
                        "required": True,
                    },
                },
                handler=self._get_regional_context,
            ),
        }

    def _get_crisis_resources(
        self,
        region: str = "NZ",
        situation_type: str = "mental_health",
    ) -> ToolResult:
        """Fetch crisis resources for a region and situation.

        Args:
            region: Region code
            situation_type: Type of crisis situation

        Returns:
            ToolResult with list of resources
        """
        try:
            region_enum = Region(region.upper())
        except ValueError:
            region_enum = self.default_region
            logger.warning(f"Unknown region '{region}', using default {self.default_region}")

        resources = self.region_manager.get_crisis_resources(region_enum, situation_type)

        # Format resources for model consumption
        formatted = []
        for resource in resources:
            formatted.append({
                "number": resource.number,
                "name": resource.name,
                "description": resource.description,
                "availability": resource.availability,
                "cost": resource.cost,
                "services": resource.services,
            })

        return ToolResult(
            success=True,
            data={
                "region": region_enum.value,
                "situation_type": situation_type,
                "resources": formatted,
                "count": len(formatted),
            },
        )

    def _log_incident(self, incident_data: Dict[str, Any]) -> ToolResult:
        """Log a crisis incident.

        Args:
            incident_data: Incident details

        Returns:
            ToolResult with incident ID
        """
        incident = {
            "incident_id": datetime.utcnow().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.utcnow().isoformat(),
            **incident_data,
        }

        self.incident_log.append(incident)

        return ToolResult(
            success=True,
            data={
                "incident_id": incident["incident_id"],
                "logged": True,
                "timestamp": incident["timestamp"],
            },
        )

    def _check_hallucination(
        self,
        number: str,
        region: str = "NZ",
    ) -> ToolResult:
        """Check if a number is hallucinated/fake.

        Args:
            number: Phone number to check
            region: Expected region

        Returns:
            ToolResult with verification status
        """
        try:
            region_enum = Region(region.upper())
        except ValueError:
            region_enum = self.default_region

        # Check if known fake
        is_fake = self.region_manager.is_known_fake(number, region_enum)

        # Check if wrong region
        correct_region = self.region_manager.is_wrong_region_number(number, region_enum)

        # Check if verified
        config = self.region_manager.get_config(region_enum)
        is_verified = any(
            r.number == number
            for r in config.crisis_resources.values()
        )

        result = {
            "number": number,
            "region": region_enum.value,
            "is_fake": is_fake,
            "is_wrong_region": correct_region is not None,
            "correct_region": correct_region,
            "is_verified": is_verified,
            "status": "verified" if is_verified else ("fake" if is_fake else ("wrong_region" if correct_region else "unknown")),
        }

        if correct_region:
            result["warning"] = f"This number ({number}) is for {correct_region}, not {region_enum.value}"

        return ToolResult(success=True, data=result)

    def _get_regional_context(self, region: str) -> ToolResult:
        """Get cultural context for a region.

        Args:
            region: Region code

        Returns:
            ToolResult with regional context
        """
        try:
            region_enum = Region(region.upper())
        except ValueError:
            return ToolResult(
                success=False,
                data=None,
                error=f"Unknown region: {region}",
            )

        config = self.region_manager.get_config(region_enum)

        return ToolResult(
            success=True,
            data={
                "region": region_enum.value,
                "country_name": config.country_name,
                "emergency_number": config.emergency_number,
                "cultural_contexts": config.cultural_contexts,
                "local_slang": config.local_slang,
            },
        )

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tools.keys())

    def get_tools_prompt(self) -> str:
        """Generate a prompt describing available tools.

        Returns:
            Formatted string describing tools for model context
        """
        prompt = "AVAILABLE TOOLS:\n"
        for name, tool in self.tools.items():
            prompt += f"\n[TOOL_CALL: {name}("
            params = []
            for param_name, param_info in tool.parameters.items():
                param_type = param_info.get("type", "string")
                required = param_info.get("required", False)
                req_str = "*" if required else ""
                params.append(f"{param_name}{req_str}: {param_type}")
            prompt += ", ".join(params)
            prompt += f")]\n  {tool.description}\n"

        return prompt


class ToolCallParser:
    """Parses tool calls from model output text."""

    # Pattern to match [TOOL_CALL: function_name(args)]
    TOOL_CALL_PATTERN = re.compile(
        r'\[TOOL_CALL:\s*(\w+)\s*\(([^)]*)\)\s*\]',
        re.IGNORECASE
    )

    @classmethod
    def parse_output(cls, output: str) -> List[ToolCall]:
        """Parse all tool calls from model output.

        Args:
            output: Model output text

        Returns:
            List of parsed tool calls
        """
        tool_calls = []

        for match in cls.TOOL_CALL_PATTERN.finditer(output):
            function_name = match.group(1)
            args_str = match.group(2)

            # Parse arguments
            arguments = cls._parse_arguments(args_str)

            tool_calls.append(ToolCall(
                name=function_name,
                arguments=arguments,
                raw_text=match.group(0),
            ))

        return tool_calls

    @classmethod
    def _parse_arguments(cls, args_str: str) -> Dict[str, Any]:
        """Parse argument string into dictionary.

        Args:
            args_str: String like "region='NZ', situation_type='mental_health'"

        Returns:
            Dict of argument name to value
        """
        arguments = {}

        if not args_str.strip():
            return arguments

        # Pattern for key='value' or key="value" or key={...}
        arg_pattern = re.compile(
            r"(\w+)\s*=\s*(?:'([^']*)'|\"([^\"]*)\"|(\{[^}]+\})|([^,\s]+))"
        )

        for match in arg_pattern.finditer(args_str):
            key = match.group(1)
            # Get the value from whichever group matched
            value = match.group(2) or match.group(3) or match.group(4) or match.group(5)

            # Try to parse as JSON if it looks like an object
            if value and value.startswith('{'):
                try:
                    value = json.loads(value.replace("'", '"'))
                except json.JSONDecodeError:
                    pass

            arguments[key] = value

        return arguments

    @classmethod
    def extract_and_remove_tool_calls(cls, output: str) -> tuple[str, List[ToolCall]]:
        """Extract tool calls and return cleaned output.

        Args:
            output: Model output text

        Returns:
            Tuple of (cleaned_output, tool_calls)
        """
        tool_calls = cls.parse_output(output)

        # Remove tool calls from output
        cleaned = cls.TOOL_CALL_PATTERN.sub('', output)
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()

        return cleaned, tool_calls


class ToolExecutor:
    """Executes parsed tool calls."""

    def __init__(self, tools: GuardianTools):
        """Initialize executor with tools.

        Args:
            tools: GuardianTools instance
        """
        self.tools = tools

    def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a single tool call.

        Args:
            tool_call: Parsed tool call

        Returns:
            Result of tool execution
        """
        import time
        start_time = time.time()

        tool = self.tools.get_tool(tool_call.name)
        if tool is None:
            return ToolResult(
                success=False,
                data=None,
                error=f"Unknown tool: {tool_call.name}",
            )

        try:
            result = tool.handler(**tool_call.arguments)
            result.execution_time_ms = (time.time() - start_time) * 1000
            return result
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    def execute_all(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute multiple tool calls.

        Args:
            tool_calls: List of tool calls to execute

        Returns:
            List of results
        """
        return [self.execute(tc) for tc in tool_calls]

    def format_results_for_context(self, results: List[ToolResult]) -> str:
        """Format tool results for adding to model context.

        Args:
            results: Tool execution results

        Returns:
            Formatted string for model context
        """
        formatted = []
        for result in results:
            if result.success:
                formatted.append(f"[TOOL_RESULT: {json.dumps(result.data)}]")
            else:
                formatted.append(f"[TOOL_ERROR: {result.error}]")

        return "\n".join(formatted)


# Convenience function for tool-augmented responses
def process_model_output_with_tools(
    output: str,
    tools: GuardianTools,
    execute_tools: bool = True,
) -> Dict[str, Any]:
    """Process model output, extracting and optionally executing tool calls.

    Args:
        output: Raw model output
        tools: GuardianTools instance
        execute_tools: Whether to execute the tool calls

    Returns:
        Dict with processed output and tool results
    """
    parser = ToolCallParser()
    executor = ToolExecutor(tools)

    # Parse tool calls
    cleaned_output, tool_calls = parser.extract_and_remove_tool_calls(output)

    result = {
        "output": cleaned_output,
        "raw_output": output,
        "tool_calls": [
            {"name": tc.name, "arguments": tc.arguments}
            for tc in tool_calls
        ],
        "tool_results": [],
    }

    # Execute tools if requested
    if execute_tools and tool_calls:
        tool_results = executor.execute_all(tool_calls)
        result["tool_results"] = [
            {
                "success": tr.success,
                "data": tr.data,
                "error": tr.error,
                "execution_time_ms": tr.execution_time_ms,
            }
            for tr in tool_results
        ]

    return result
