"""Stack Overflow MCP Server implementation using fastmcp."""

import os
from typing import Any, Dict

from fastmcp import FastMCP

from stack_overflow_mcp_light.logging_config import get_logger, setup_logging
from stack_overflow_mcp_light.models import (
    AnswerDetailsRequest,
    AnswerSearchRequest,
    QuestionDetailsRequest,
    QuestionsByTagRequest,
    QuestionSearchRequest,
)
from stack_overflow_mcp_light.tools.answers import AnswersClient
from stack_overflow_mcp_light.tools.questions import QuestionsClient

logger = get_logger(__name__)

# Initialize MCP server
mcp: FastMCP = FastMCP("Stack Overflow MCP Server")

# Initialize specialized clients
questions_client = QuestionsClient()
answers_client = AnswersClient()


@mcp.tool()
async def search_questions(request: QuestionSearchRequest) -> Dict[str, Any]:
    """
    Search Stack Overflow questions using advanced filters.

    Args:
        request: Question search request with filters and pagination

    Returns:
        Search results with questions matching the criteria
    """
    try:
        return await questions_client.search_questions(
            q=request.q,
            tagged=request.tagged,
            intitle=request.intitle,
            nottagged=request.nottagged,
            body=request.body,
            accepted=request.accepted,
            closed=request.closed,
            answers=request.answers,
            views=request.views,
            sort=request.sort.value,
            order=request.order.value,
            page=request.page,
            page_size=request.page_size,
        )
    except Exception as e:
        logger.error(f"Error searching questions: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_question_details(request: QuestionDetailsRequest) -> Dict[str, Any]:
    """
    Get detailed information about a specific Stack Overflow question.

    Args:
        request: Question details request with ID and inclusion options

    Returns:
        Detailed question information including body, answers, and optionally comments
    """
    try:
        return await questions_client.get_question_details(
            question_id=request.question_id,
            include_body=request.include_body,
            include_comments=request.include_comments,
            include_answers=request.include_answers,
        )
    except Exception as e:
        logger.error(f"Error getting question details: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_questions_by_tag(request: QuestionsByTagRequest) -> Dict[str, Any]:
    """
    Get Stack Overflow questions that have a specific tag.

    Args:
        request: Request with tag name, sort options, and pagination

    Returns:
        Questions that have the specified tag
    """
    try:
        return await questions_client.get_questions_by_tag(
            tag=request.tag,
            sort=request.sort.value,
            order=request.order.value,
            page=request.page,
            page_size=request.page_size,
        )
    except Exception as e:
        logger.error(f"Error getting questions by tag: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_question_answers(request: QuestionDetailsRequest) -> Dict[str, Any]:
    """
    Get answers for a specific Stack Overflow question.

    Args:
        request: Question details request (using question_id)

    Returns:
        Answers for the specified question
    """
    try:
        return await questions_client.get_question_answers(
            question_id=request.question_id, page=1, page_size=30
        )
    except Exception as e:
        logger.error(f"Error getting question answers: {e}")
        return {"error": str(e)}


@mcp.tool()
async def search_answers(request: AnswerSearchRequest) -> Dict[str, Any]:
    """
    Search Stack Overflow answers using text search.

    Args:
        request: Answer search request with query and pagination

    Returns:
        Search results with answers matching the query
    """
    try:
        return await answers_client.search_answers(
            q=request.q,
            sort=request.sort.value,
            order=request.order.value,
            page=request.page,
            page_size=request.page_size,
        )
    except Exception as e:
        logger.error(f"Error searching answers: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_answer_details(request: AnswerDetailsRequest) -> Dict[str, Any]:
    """
    Get detailed information about a specific Stack Overflow answer.

    Args:
        request: Answer details request with ID and inclusion options

    Returns:
        Detailed answer information including body and optionally comments
    """
    try:
        return await answers_client.get_answer_details(
            answer_id=request.answer_id,
            include_body=request.include_body,
            include_comments=request.include_comments,
        )
    except Exception as e:
        logger.error(f"Error getting answer details: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_top_answers() -> Dict[str, Any]:
    """
    Get top-voted answers from Stack Overflow.

    Returns:
        Top answers sorted by votes
    """
    try:
        return await answers_client.get_top_answers(
            sort="votes", order="desc", page=1, page_size=30
        )
    except Exception as e:
        logger.error(f"Error getting top answers: {e}")
        return {"error": str(e)}


def main() -> None:
    """Main entry point for the MCP server."""
    show_logs = os.getenv("STACK_OVERFLOW_MCP_SHOW_LOGS", "false").lower() == "true"
    setup_logging(include_console=show_logs)

    # API key is optional
    api_key = os.getenv("STACK_EXCHANGE_API_KEY")
    if api_key:
        logger.info("Starting Stack Overflow MCP Server with API key...")
    else:
        logger.info(
            "Starting Stack Overflow MCP Server without API key (rate limited)..."
        )

    # Run the server
    mcp.run(show_banner=False)


if __name__ == "__main__":
    main()
