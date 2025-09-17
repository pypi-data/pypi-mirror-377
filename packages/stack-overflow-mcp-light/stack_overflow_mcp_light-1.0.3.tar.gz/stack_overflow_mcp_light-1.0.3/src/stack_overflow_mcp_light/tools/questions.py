"""Questions client for Stack Exchange API operations."""

from typing import Any, Dict, Optional

from stack_overflow_mcp_light.logging_config import get_logger
from stack_overflow_mcp_light.tools.base_client import BaseStackExchangeClient

logger = get_logger(__name__)


class QuestionsClient(BaseStackExchangeClient):
    """Client for question-related Stack Exchange API operations."""

    def __init__(self) -> None:
        """Initialize the questions client."""
        super().__init__()

    async def search_questions(
        self,
        q: Optional[str] = None,
        tagged: Optional[str] = None,
        intitle: Optional[str] = None,
        nottagged: Optional[str] = None,
        body: Optional[str] = None,
        accepted: Optional[bool] = None,
        closed: Optional[bool] = None,
        answers: Optional[int] = None,
        views: Optional[int] = None,
        sort: str = "activity",
        order: str = "desc",
        page: int = 1,
        page_size: int = 30,
    ) -> Dict[str, Any]:
        """
        Search questions using advanced search parameters.

        Args:
            q: Free-form text search
            tagged: Semi-colon delimited list of tags
            intitle: Search in question titles
            nottagged: Exclude these tags
            body: Text in question body
            accepted: Has accepted answer
            closed: Question is closed
            answers: Minimum number of answers
            views: Minimum view count
            sort: Sort criteria
            order: Sort order
            page: Page number
            page_size: Items per page

        Returns:
            Search results with questions
        """
        params = {"sort": sort, "order": order}

        # Add search parameters if provided
        if q:
            params["q"] = q
        if tagged:
            params["tagged"] = tagged
        if intitle:
            params["intitle"] = intitle
        if nottagged:
            params["nottagged"] = nottagged
        if body:
            params["body"] = body
        if accepted is not None:
            params["accepted"] = str(accepted).lower()
        if closed is not None:
            params["closed"] = str(closed).lower()
        if answers is not None:
            params["answers"] = str(answers)
        if views is not None:
            params["views"] = str(views)

        try:
            # Use advanced search if we have complex parameters, otherwise basic search
            if (
                q
                or body
                or accepted is not None
                or closed is not None
                or answers
                or views
            ):
                endpoint = "/search/advanced"
            else:
                endpoint = "/search"

            logger.info(f"Searching questions with params: {params}")

            return await self._paginated_request(endpoint, params, page, page_size)

        except Exception as e:
            logger.error(f"Error searching questions: {e}")
            raise

    async def get_question_details(
        self,
        question_id: int,
        include_body: bool = True,
        include_comments: bool = False,
        include_answers: bool = True,
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific question.

        Args:
            question_id: Question ID
            include_body: Include question body
            include_comments: Include comments
            include_answers: Include answers

        Returns:
            Question details
        """
        params = {}

        # Build filter parameter for what to include
        filters = []
        if include_body:
            filters.append("withbody")
        if include_comments:
            filters.append("comments")
        if include_answers:
            filters.append("answers")

        if filters:
            # Use a custom filter or default that includes body
            params["filter"] = "!nKzQUR3Egv"  # Includes body, answers, and comments

        try:
            endpoint = f"/questions/{question_id}"

            logger.info(f"Getting question details for ID: {question_id}")

            result = await self._make_request(endpoint, params)

            # If we want answers, also get them separately if not included
            if include_answers and "items" in result and len(result["items"]) > 0:
                question = result["items"][0]
                if "answers" not in question or not question["answers"]:
                    # Get answers separately
                    answers_result = await self._make_request(
                        f"/questions/{question_id}/answers",
                        {"filter": "!nKzQUR3Egv" if include_body else None},
                    )
                    if "items" in answers_result:
                        question["answers"] = answers_result["items"]

            return result

        except Exception as e:
            logger.error(f"Error getting question details: {e}")
            raise

    async def get_questions_by_tag(
        self,
        tag: str,
        sort: str = "activity",
        order: str = "desc",
        page: int = 1,
        page_size: int = 30,
    ) -> Dict[str, Any]:
        """
        Get questions that have a specific tag.

        Args:
            tag: Tag name
            sort: Sort criteria
            order: Sort order
            page: Page number
            page_size: Items per page

        Returns:
            Questions with the specified tag
        """
        params = {"tagged": tag, "sort": sort, "order": order}

        try:
            logger.info(f"Getting questions for tag: {tag}")

            return await self._paginated_request("/questions", params, page, page_size)

        except Exception as e:
            logger.error(f"Error getting questions by tag: {e}")
            raise

    async def get_question_answers(
        self,
        question_id: int,
        sort: str = "votes",
        order: str = "desc",
        page: int = 1,
        page_size: int = 30,
    ) -> Dict[str, Any]:
        """
        Get answers for a specific question.

        Args:
            question_id: Question ID
            sort: Sort criteria
            order: Sort order
            page: Page number
            page_size: Items per page

        Returns:
            Answers for the question
        """
        params = {"sort": sort, "order": order, "filter": "!nKzQUR3Egv"}  # Include body

        try:
            endpoint = f"/questions/{question_id}/answers"

            logger.info(f"Getting answers for question ID: {question_id}")

            return await self._paginated_request(endpoint, params, page, page_size)

        except Exception as e:
            logger.error(f"Error getting question answers: {e}")
            raise
