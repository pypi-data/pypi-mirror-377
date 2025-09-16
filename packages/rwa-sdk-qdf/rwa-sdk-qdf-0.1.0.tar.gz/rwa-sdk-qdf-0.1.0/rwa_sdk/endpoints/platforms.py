"""
RWA.xyz SDK Platforms Endpoint
Handle platform-related operations
"""

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..client import RWAClient


class RWAPlatforms:
    """Handle platform-related operations"""

    def __init__(self, client: 'RWAClient'):
        """
        Initialize platforms endpoint

        Args:
            client: The main RWA client instance
        """
        self.client = client

    async def get_platform(self, platform_slug: str) -> Dict:
        """
        Get details for a specific platform

        Args:
            platform_slug: The slug identifier for the platform

        Returns:
            Platform details dictionary
        """
        endpoint = f"/_next/data/{self.client.build_id}/platforms/{platform_slug}.json"
        params = {"platformSlug": platform_slug}
        return await self.client._request("GET", endpoint, params=params)

    async def list_platforms(self) -> Dict:
        """
        List all platforms

        Returns:
            List of all platforms
        """
        endpoint = f"/_next/data/{self.client.build_id}/platforms.json"
        return await self.client._request("GET", endpoint)