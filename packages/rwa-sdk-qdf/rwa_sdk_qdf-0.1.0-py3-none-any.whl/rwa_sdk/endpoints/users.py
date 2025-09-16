"""
RWA.xyz SDK Users Endpoint
Handle user-related operations
"""

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..client import RWAClient


class RWAUsers:
    """Handle user-related operations"""

    def __init__(self, client: 'RWAClient'):
        """
        Initialize users endpoint

        Args:
            client: The main RWA client instance
        """
        self.client = client

    async def get_profile(self) -> Dict:
        """
        Get current user profile

        Returns:
            User profile dictionary
        """
        endpoint = "/api/trpc/users.getProfile"
        return await self.client._request("GET", endpoint)

    async def get_session(self) -> Dict:
        """
        Get current authentication session

        Returns:
            Session details dictionary
        """
        endpoint = "/api/auth/session"
        return await self.client._request("GET", endpoint)