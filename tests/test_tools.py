"""Tests for the Guardian LLM tool system."""

import pytest

from guardian_llm.tools import (
    GuardianTools,
    ToolCall,
    ToolResult,
    ToolCallParser,
    ToolExecutor,
    process_model_output_with_tools,
)
from guardian_llm.regions import Region


class TestToolCallParser:
    """Tests for parsing tool calls from model output."""

    def test_parse_simple_tool_call(self):
        """Test parsing a simple tool call."""
        output = "[TOOL_CALL: get_crisis_resources(region='NZ')]"
        tool_calls = ToolCallParser.parse_output(output)

        assert len(tool_calls) == 1
        assert tool_calls[0].name == "get_crisis_resources"
        assert tool_calls[0].arguments.get("region") == "NZ"

    def test_parse_tool_call_multiple_args(self):
        """Test parsing tool call with multiple arguments."""
        output = "[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='crisis')]"
        tool_calls = ToolCallParser.parse_output(output)

        assert len(tool_calls) == 1
        assert tool_calls[0].arguments.get("region") == "NZ"
        assert tool_calls[0].arguments.get("situation_type") == "crisis"

    def test_parse_multiple_tool_calls(self):
        """Test parsing multiple tool calls in output."""
        output = """Here is my response.

[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='emergency')]

I recommend these resources.

[TOOL_CALL: check_hallucination(number='111', region='NZ')]"""

        tool_calls = ToolCallParser.parse_output(output)

        assert len(tool_calls) == 2
        assert tool_calls[0].name == "get_crisis_resources"
        assert tool_calls[1].name == "check_hallucination"

    def test_parse_tool_call_with_double_quotes(self):
        """Test parsing tool call with double quotes."""
        output = '[TOOL_CALL: get_crisis_resources(region="AU")]'
        tool_calls = ToolCallParser.parse_output(output)

        assert len(tool_calls) == 1
        assert tool_calls[0].arguments.get("region") == "AU"

    def test_parse_no_tool_calls(self):
        """Test parsing output with no tool calls."""
        output = "This is just a normal response without any tool calls."
        tool_calls = ToolCallParser.parse_output(output)

        assert len(tool_calls) == 0

    def test_parse_case_insensitive(self):
        """Test tool call parsing is case insensitive."""
        output = "[tool_call: get_crisis_resources(region='NZ')]"
        tool_calls = ToolCallParser.parse_output(output)

        assert len(tool_calls) == 1

    def test_extract_and_remove_tool_calls(self):
        """Test extracting tool calls and cleaning output."""
        output = """RISK LEVEL: HIGH
PATTERNS DETECTED: suicide ideation

[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='crisis')]

I hear that you're struggling."""

        cleaned, tool_calls = ToolCallParser.extract_and_remove_tool_calls(output)

        assert len(tool_calls) == 1
        assert "[TOOL_CALL" not in cleaned
        assert "RISK LEVEL: HIGH" in cleaned
        assert "I hear that you're struggling" in cleaned


class TestGuardianTools:
    """Tests for GuardianTools class."""

    @pytest.fixture
    def tools(self):
        """Create tools instance for testing."""
        return GuardianTools(default_region=Region.NZ)

    def test_list_tools(self, tools):
        """Test listing available tools."""
        tool_names = tools.list_tools()

        assert "get_crisis_resources" in tool_names
        assert "log_incident" in tool_names
        assert "check_hallucination" in tool_names
        assert "get_regional_context" in tool_names

    def test_get_tool(self, tools):
        """Test getting a tool by name."""
        tool = tools.get_tool("get_crisis_resources")

        assert tool is not None
        assert tool.name == "get_crisis_resources"
        assert "region" in tool.parameters

    def test_get_nonexistent_tool(self, tools):
        """Test getting a nonexistent tool."""
        tool = tools.get_tool("nonexistent_tool")
        assert tool is None

    def test_get_crisis_resources_tool(self, tools):
        """Test executing get_crisis_resources tool."""
        result = tools._get_crisis_resources(region="NZ", situation_type="mental_health")

        assert result.success is True
        assert result.data["region"] == "NZ"
        assert result.data["count"] > 0
        assert len(result.data["resources"]) > 0

        # Check resource structure
        resource = result.data["resources"][0]
        assert "number" in resource
        assert "name" in resource

    def test_get_crisis_resources_default_region(self, tools):
        """Test get_crisis_resources uses default region."""
        result = tools._get_crisis_resources()

        assert result.success is True
        assert result.data["region"] == "NZ"  # default

    def test_get_crisis_resources_unknown_region(self, tools):
        """Test get_crisis_resources with unknown region falls back."""
        result = tools._get_crisis_resources(region="INVALID")

        assert result.success is True
        assert result.data["region"] == "NZ"  # falls back to default

    def test_check_hallucination_verified(self, tools):
        """Test checking a verified number."""
        result = tools._check_hallucination(number="1737", region="NZ")

        assert result.success is True
        assert result.data["is_verified"] is True
        assert result.data["is_fake"] is False

    def test_check_hallucination_fake(self, tools):
        """Test checking a known fake number."""
        result = tools._check_hallucination(number="0800 543 800", region="NZ")

        assert result.success is True
        assert result.data["is_fake"] is True
        assert result.data["status"] == "fake"

    def test_check_hallucination_wrong_region(self, tools):
        """Test checking a wrong-region number."""
        result = tools._check_hallucination(number="988", region="NZ")

        assert result.success is True
        assert result.data["is_wrong_region"] is True
        assert result.data["correct_region"] == "US"
        assert "warning" in result.data

    def test_get_regional_context(self, tools):
        """Test getting regional context."""
        result = tools._get_regional_context(region="NZ")

        assert result.success is True
        assert result.data["country_name"] == "New Zealand"
        assert result.data["emergency_number"] == "111"
        assert len(result.data["cultural_contexts"]) > 0

    def test_get_regional_context_unknown_region(self, tools):
        """Test getting regional context for unknown region."""
        result = tools._get_regional_context(region="INVALID")

        assert result.success is False
        assert result.error is not None

    def test_log_incident(self, tools):
        """Test logging an incident."""
        incident_data = {
            "type": "suicide_ideation",
            "severity": "HIGH",
            "region": "NZ",
        }
        result = tools._log_incident(incident_data=incident_data)

        assert result.success is True
        assert "incident_id" in result.data
        assert result.data["logged"] is True

    def test_get_tools_prompt(self, tools):
        """Test generating tools prompt."""
        prompt = tools.get_tools_prompt()

        assert "AVAILABLE TOOLS" in prompt
        assert "get_crisis_resources" in prompt
        assert "[TOOL_CALL:" in prompt


class TestToolExecutor:
    """Tests for ToolExecutor class."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        tools = GuardianTools(default_region=Region.NZ)
        return ToolExecutor(tools)

    def test_execute_valid_tool(self, executor):
        """Test executing a valid tool call."""
        tool_call = ToolCall(
            name="get_crisis_resources",
            arguments={"region": "NZ", "situation_type": "mental_health"},
        )
        result = executor.execute(tool_call)

        assert result.success is True
        assert result.data is not None
        assert result.execution_time_ms >= 0

    def test_execute_unknown_tool(self, executor):
        """Test executing an unknown tool."""
        tool_call = ToolCall(name="unknown_tool", arguments={})
        result = executor.execute(tool_call)

        assert result.success is False
        assert "Unknown tool" in result.error

    def test_execute_all(self, executor):
        """Test executing multiple tool calls."""
        tool_calls = [
            ToolCall(name="get_crisis_resources", arguments={"region": "NZ"}),
            ToolCall(name="check_hallucination", arguments={"number": "1737", "region": "NZ"}),
        ]
        results = executor.execute_all(tool_calls)

        assert len(results) == 2
        assert all(r.success for r in results)

    def test_format_results_for_context(self, executor):
        """Test formatting results for model context."""
        results = [
            ToolResult(success=True, data={"count": 5}),
            ToolResult(success=False, data=None, error="Test error"),
        ]
        formatted = executor.format_results_for_context(results)

        assert "[TOOL_RESULT:" in formatted
        assert "[TOOL_ERROR:" in formatted
        assert "Test error" in formatted


class TestProcessModelOutput:
    """Tests for the process_model_output_with_tools function."""

    @pytest.fixture
    def tools(self):
        return GuardianTools(default_region=Region.NZ)

    def test_process_with_tool_calls(self, tools):
        """Test processing output with tool calls."""
        output = """RISK LEVEL: HIGH
PATTERNS DETECTED: hopelessness

[TOOL_CALL: get_crisis_resources(region='NZ', situation_type='crisis')]

Please reach out for help."""

        result = process_model_output_with_tools(output, tools, execute_tools=True)

        assert "RISK LEVEL: HIGH" in result["output"]
        assert "[TOOL_CALL" not in result["output"]
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["name"] == "get_crisis_resources"
        assert len(result["tool_results"]) == 1
        assert result["tool_results"][0]["success"] is True

    def test_process_without_executing(self, tools):
        """Test processing without executing tools."""
        output = "[TOOL_CALL: get_crisis_resources(region='NZ')]"

        result = process_model_output_with_tools(output, tools, execute_tools=False)

        assert len(result["tool_calls"]) == 1
        assert len(result["tool_results"]) == 0

    def test_process_no_tool_calls(self, tools):
        """Test processing output without tool calls."""
        output = "RISK LEVEL: LOW\nNo immediate concern detected."

        result = process_model_output_with_tools(output, tools)

        assert result["output"] == output
        assert len(result["tool_calls"]) == 0
        assert len(result["tool_results"]) == 0


class TestToolCallDataclass:
    """Tests for ToolCall dataclass."""

    def test_create_tool_call(self):
        """Test creating a tool call."""
        tc = ToolCall(
            name="get_crisis_resources",
            arguments={"region": "NZ"},
            raw_text="[TOOL_CALL: get_crisis_resources(region='NZ')]",
        )

        assert tc.name == "get_crisis_resources"
        assert tc.arguments["region"] == "NZ"
        assert "[TOOL_CALL" in tc.raw_text

    def test_tool_call_default_raw_text(self):
        """Test tool call with default raw_text."""
        tc = ToolCall(name="test", arguments={})
        assert tc.raw_text == ""


class TestToolResultDataclass:
    """Tests for ToolResult dataclass."""

    def test_create_success_result(self):
        """Test creating a success result."""
        result = ToolResult(success=True, data={"count": 5})

        assert result.success is True
        assert result.data["count"] == 5
        assert result.error is None

    def test_create_error_result(self):
        """Test creating an error result."""
        result = ToolResult(success=False, data=None, error="Something went wrong")

        assert result.success is False
        assert result.error == "Something went wrong"

    def test_result_execution_time(self):
        """Test result with execution time."""
        result = ToolResult(success=True, data={}, execution_time_ms=15.5)

        assert result.execution_time_ms == 15.5
