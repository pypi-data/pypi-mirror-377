"""Answers client for Stack Exchange API operations."""

from typing import Any, Dict, Optional

from stack_overflow_mcp_light.logging_config import get_logger
from stack_overflow_mcp_light.tools.base_client import BaseStackExchangeClient

logger = get_logger(__name__)


class AnswersClient(BaseStackExchangeClient):
    """Client for answer-related Stack Exchange API operations."""

    def __init__(self) -> None:
        """Initialize the answers client."""
        super().__init__()

    async def search_answers(
        self,
        q: Optional[str] = None,
        sort: str = "activity",
        order: str = "desc",
        page: int = 1,
        page_size: int = 30,
    ) -> Dict[str, Any]:
        """
        Search answers using text search.

        Args:
            q: Free-form text search
            sort: Sort criteria
            order: Sort order
            page: Page number
            page_size: Items per page

        Returns:
            Search results with answers
        """
        params = {"sort": sort, "order": order, "filter": "!nKzQUR3Egv"}  # Include body

        if q:
            params["q"] = q

        try:
            endpoint = "/search/answers" if q else "/answers"

            logger.info(f"Searching answers with query: {q or 'all answers'}")

            return await self._paginated_request(endpoint, params, page, page_size)

        except Exception as e:
            logger.error(f"Error searching answers: {e}")
            raise

    async def get_answer_details(
        self, answer_id: int, include_body: bool = True, include_comments: bool = False
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific answer.

        Args:
            answer_id: Answer ID
            include_body: Include answer body
            include_comments: Include comments

        Returns:
            Answer details
        """
        params = {}

        # Build filter parameter for what to include
        if include_body:
            params["filter"] = "!nKzQUR3Egv"  # Include body

        if include_comments:
            # Use filter that includes comments
            params["filter"] = "!)rTkrXnCGaR.8sVt"

        try:
            endpoint = f"/answers/{answer_id}"

            logger.info(f"Getting answer details for ID: {answer_id}")

            return await self._make_request(endpoint, params)

        except Exception as e:
            logger.error(f"Error getting answer details: {e}")
            raise

    async def get_answers_by_ids(
        self,
        answer_ids: list[int],
        include_body: bool = True,
        include_comments: bool = False,
    ) -> Dict[str, Any]:
        """
        Get multiple answers by their IDs.

        Args:
            answer_ids: List of answer IDs
            include_body: Include answer bodies
            include_comments: Include comments

        Returns:
            Multiple answer details
        """
        if not answer_ids:
            raise ValueError("At least one answer ID must be provided")

        params = {}

        # Build filter parameter
        if include_body:
            params["filter"] = "!nKzQUR3Egv"

        if include_comments:
            params["filter"] = "!)rTkrXnCGaR.8sVt"

        try:
            # Join IDs with semicolons for vectorized request
            ids_str = ";".join(map(str, answer_ids))
            endpoint = f"/answers/{ids_str}"

            logger.info(f"Getting details for {len(answer_ids)} answers")

            return await self._make_request(endpoint, params)

        except Exception as e:
            logger.error(f"Error getting answer details: {e}")
            raise

    async def get_top_answers(
        self,
        sort: str = "votes",
        order: str = "desc",
        page: int = 1,
        page_size: int = 30,
        min_votes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get top answers from Stack Overflow.

        Args:
            sort: Sort criteria (votes, activity, creation)
            order: Sort order
            page: Page number
            page_size: Items per page
            min_votes: Minimum vote count

        Returns:
            Top answers
        """
        params = {"sort": sort, "order": order, "filter": "!nKzQUR3Egv"}

        if min_votes is not None:
            params["min"] = str(min_votes)

        try:
            logger.info(f"Getting top answers (sort: {sort}, min_votes: {min_votes})")

            return await self._paginated_request("/answers", params, page, page_size)

        except Exception as e:
            logger.error(f"Error getting top answers: {e}")
            raise
