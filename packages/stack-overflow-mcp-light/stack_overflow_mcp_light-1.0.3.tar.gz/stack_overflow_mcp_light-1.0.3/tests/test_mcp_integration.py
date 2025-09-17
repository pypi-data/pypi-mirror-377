"""Integration tests for MCP server functionality."""

import os
from unittest.mock import patch

from fastmcp import FastMCP

from stack_overflow_mcp_light.server import main, mcp


class TestMCPServerIntegration:
    """Test MCP server integration and tool registration."""

    def test_mcp_server_creation(self):
        """Test that MCP server is created correctly."""
        assert isinstance(mcp, FastMCP)
        assert mcp.name == "Stack Overflow MCP Server"

    def test_all_tools_registered(self):
        """Test that all expected tools are registered with the MCP server."""
        expected_tools = {
            # Question tools
            "search_questions",
            "get_question_details",
            "get_questions_by_tag",
            "get_question_answers",
            # Answer tools
            "search_answers",
            "get_answer_details",
            "get_top_answers",
        }

        # Get registered tool names using the correct FastMCP API
        registered_tools = set(mcp._tool_manager._tools.keys())

        # Check that all expected tools are registered
        missing_tools = expected_tools - registered_tools
        extra_tools = registered_tools - expected_tools

        assert not missing_tools, f"Missing tools: {missing_tools}"
        assert not extra_tools, f"Unexpected tools: {extra_tools}"
        assert registered_tools == expected_tools

    @patch.dict(os.environ, {"STACK_EXCHANGE_API_KEY": "test_key"})
    @patch("stack_overflow_mcp_light.server.mcp.run")
    @patch("stack_overflow_mcp_light.server.logger")
    def test_main_with_env_vars(self, mock_logger, mock_run):
        """Test main function with API key environment variable."""
        main()

        mock_logger.info.assert_called_with(
            "Starting Stack Overflow MCP Server with API key..."
        )
        mock_run.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    @patch("stack_overflow_mcp_light.server.mcp.run")
    @patch("stack_overflow_mcp_light.server.logger")
    def test_main_without_env_vars(self, mock_logger, mock_run):
        """Test main function without API key environment variable."""
        main()

        mock_logger.info.assert_called_with(
            "Starting Stack Overflow MCP Server without API key (rate limited)..."
        )
        mock_run.assert_called_once()

    def test_tool_docstrings(self):
        """Test that all tools have proper docstrings."""
        for tool_name, tool in mcp._tool_manager._tools.items():
            func = tool.fn
            assert func.__doc__ is not None, f"Tool {tool_name} missing docstring"
            assert (
                len(func.__doc__.strip()) > 0
            ), f"Tool {tool_name} has empty docstring"

            # Check that docstring contains Returns section
            docstring = func.__doc__
            assert "Returns:" in docstring, f"Tool {tool_name} missing Returns section"

            # Check if function takes parameters and ensure Args section exists if it does
            import inspect

            sig = inspect.signature(func)
            if len(sig.parameters) > 0:
                assert (
                    "Args:" in docstring
                ), f"Tool {tool_name} takes parameters but missing Args section"

    def test_tool_request_models(self):
        """Test that all tools use proper request models for validation."""
        import inspect

        from pydantic import BaseModel

        for tool_name, tool in mcp._tool_manager._tools.items():
            func = tool.fn
            sig = inspect.signature(func)

            # Skip tools with no parameters (like get_top_answers)
            if len(sig.parameters) == 0:
                continue

            # Check that the first parameter is a Pydantic model
            first_param = list(sig.parameters.values())[0]
            param_type = first_param.annotation

            # Handle both direct class and generic types
            if hasattr(param_type, "__origin__"):
                # For generic types, get the actual class
                actual_type = (
                    param_type.__args__[0] if param_type.__args__ else param_type
                )
            else:
                actual_type = param_type

            assert inspect.isclass(actual_type) and issubclass(
                actual_type, BaseModel
            ), f"Tool {tool_name} should use Pydantic model for request validation"
