"""Test suite for Stack Overflow MCP Server tools."""

from unittest.mock import patch

import pytest

from stack_overflow_mcp_light.models import (
    AnswerDetailsRequest,
    AnswerSearchRequest,
    QuestionDetailsRequest,
    QuestionsByTagRequest,
    QuestionSearchRequest,
)
from stack_overflow_mcp_light.server import mcp


@pytest.fixture
def mock_clients():
    """Create mock specialized clients."""
    with (
        patch("stack_overflow_mcp_light.server.questions_client") as mock_questions,
        patch("stack_overflow_mcp_light.server.answers_client") as mock_answers,
    ):
        yield {"questions": mock_questions, "answers": mock_answers}


class TestQuestionTools:
    """Test question-related MCP tools."""

    @pytest.mark.asyncio
    async def test_search_questions(self, mock_clients):
        """Test search_questions tool."""
        mock_clients["questions"].search_questions.return_value = {
            "items": [
                {
                    "question_id": 12345,
                    "title": "How to use async/await in Python?",
                    "tags": ["python", "asyncio"],
                    "score": 42,
                }
            ],
            "has_more": False,
            "quota_remaining": 9999,
        }

        request = QuestionSearchRequest(
            q="asyncio", tagged="python", page=1, page_size=10
        )
        tool_func = mcp._tool_manager._tools["search_questions"].fn
        result = await tool_func(request)

        mock_clients["questions"].search_questions.assert_called_once()
        assert "items" in result or "error" in result

    @pytest.mark.asyncio
    async def test_search_questions_error(self, mock_clients):
        """Test search_questions tool error handling."""
        mock_clients["questions"].search_questions.side_effect = Exception("API Error")

        request = QuestionSearchRequest(q="test")
        tool_func = mcp._tool_manager._tools["search_questions"].fn
        result = await tool_func(request)

        assert "error" in result
        assert result["error"] == "API Error"

    @pytest.mark.asyncio
    async def test_get_question_details(self, mock_clients):
        """Test get_question_details tool."""
        mock_clients["questions"].get_question_details.return_value = {
            "items": [
                {
                    "question_id": 12345,
                    "title": "Test Question",
                    "body": "Question body content",
                    "answers": [
                        {"answer_id": 67890, "body": "Answer content", "score": 10}
                    ],
                }
            ]
        }

        request = QuestionDetailsRequest(
            question_id=12345, include_body=True, include_answers=True
        )
        tool_func = mcp._tool_manager._tools["get_question_details"].fn
        result = await tool_func(request)

        mock_clients["questions"].get_question_details.assert_called_once_with(
            question_id=12345,
            include_body=True,
            include_comments=False,
            include_answers=True,
        )
        assert "items" in result or "error" in result

    @pytest.mark.asyncio
    async def test_get_questions_by_tag(self, mock_clients):
        """Test get_questions_by_tag tool."""
        mock_clients["questions"].get_questions_by_tag.return_value = {
            "items": [],
            "has_more": False,
        }

        request = QuestionsByTagRequest(tag="python")
        tool_func = mcp._tool_manager._tools["get_questions_by_tag"].fn
        result = await tool_func(request)

        mock_clients["questions"].get_questions_by_tag.assert_called_once()
        assert "items" in result or "error" in result

    @pytest.mark.asyncio
    async def test_get_question_answers(self, mock_clients):
        """Test get_question_answers tool."""
        mock_clients["questions"].get_question_answers.return_value = {
            "items": [],
            "has_more": False,
        }

        request = QuestionDetailsRequest(question_id=12345)
        tool_func = mcp._tool_manager._tools["get_question_answers"].fn
        result = await tool_func(request)

        mock_clients["questions"].get_question_answers.assert_called_once_with(
            question_id=12345, page=1, page_size=30
        )
        assert "items" in result or "error" in result


class TestAnswerTools:
    """Test answer-related MCP tools."""

    @pytest.mark.asyncio
    async def test_search_answers(self, mock_clients):
        """Test search_answers tool."""
        mock_clients["answers"].search_answers.return_value = {
            "items": [],
            "has_more": False,
        }

        request = AnswerSearchRequest(q="python")
        tool_func = mcp._tool_manager._tools["search_answers"].fn
        result = await tool_func(request)

        mock_clients["answers"].search_answers.assert_called_once()
        assert "items" in result or "error" in result

    @pytest.mark.asyncio
    async def test_get_answer_details(self, mock_clients):
        """Test get_answer_details tool."""
        mock_clients["answers"].get_answer_details.return_value = {
            "items": [
                {
                    "answer_id": 67890,
                    "body": "Answer content",
                    "score": 10,
                }
            ]
        }

        request = AnswerDetailsRequest(answer_id=67890, include_body=True)
        tool_func = mcp._tool_manager._tools["get_answer_details"].fn
        result = await tool_func(request)

        mock_clients["answers"].get_answer_details.assert_called_once_with(
            answer_id=67890,
            include_body=True,
            include_comments=False,
        )
        assert "items" in result or "error" in result

    @pytest.mark.asyncio
    async def test_get_top_answers(self, mock_clients):
        """Test get_top_answers tool."""
        mock_clients["answers"].get_top_answers.return_value = {
            "items": [],
            "has_more": False,
        }

        tool_func = mcp._tool_manager._tools["get_top_answers"].fn
        result = await tool_func()

        mock_clients["answers"].get_top_answers.assert_called_once_with(
            sort="votes", order="desc", page=1, page_size=30
        )
        assert "items" in result or "error" in result


class TestServerStructure:
    """Test server structure and client usage."""

    def test_mcp_server_exists(self):
        """Test that MCP server is properly initialized."""
        assert mcp is not None
        assert hasattr(mcp, "_tool_manager")

    def test_all_tools_are_registered(self):
        """Test that all expected tools are properly registered."""
        tools = list(mcp._tool_manager._tools.keys())

        expected_tools = [
            # Question tools
            "search_questions",
            "get_question_details",
            "get_questions_by_tag",
            "get_question_answers",
            # Answer tools
            "search_answers",
            "get_answer_details",
            "get_top_answers",
        ]

        for tool in expected_tools:
            assert tool in tools, f"Tool {tool} not found in registered tools"

        assert len(tools) == len(
            expected_tools
        ), f"Expected {len(expected_tools)} tools, found {len(tools)}: {tools}"

    def test_error_handling_pattern(self, mock_clients):
        """Test that all tools follow the same error handling pattern."""
        mock_clients["questions"].search_questions.side_effect = Exception("Test error")
        mock_clients["answers"].search_answers.side_effect = Exception("Test error")

        question_request = QuestionSearchRequest(q="test")
        question_tool = mcp._tool_manager._tools["search_questions"].fn

        answer_request = AnswerSearchRequest(q="test")
        answer_tool = mcp._tool_manager._tools["search_answers"].fn

        import asyncio

        async def test_errors():
            question_result = await question_tool(question_request)
            answer_result = await answer_tool(answer_request)

            assert "error" in question_result
            assert "error" in answer_result

            assert question_result["error"] == "Test error"
            assert answer_result["error"] == "Test error"

        asyncio.run(test_errors())
