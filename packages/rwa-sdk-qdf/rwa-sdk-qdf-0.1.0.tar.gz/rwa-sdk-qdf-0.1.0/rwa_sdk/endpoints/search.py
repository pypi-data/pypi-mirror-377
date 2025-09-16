"""
RWA.xyz SDK Search Endpoint
Handle search operations
"""

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..client import RWAClient


class RWASearch:
    """Handle search operations"""

    def __init__(self, client: 'RWAClient'):
        """
        Initialize search endpoint

        Args:
            client: The main RWA client instance
        """
        self.client = client

    async def get_initial_search_groups(self) -> Dict:
        """
        Get initial search groups for search interface

        Returns:
            Search groups dictionary
        """
        endpoint = "/api/trpc/search.getInitialSearchGroups"
        params = {"batch": "1", "input": "{}"}
        return await self.client._request("GET", endpoint, params=params)