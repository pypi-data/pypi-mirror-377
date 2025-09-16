"""
RWA.xyz SDK Networks Endpoint
Handle network-related operations
"""

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..client import RWAClient


class RWANetworks:
    """Handle network-related operations"""

    def __init__(self, client: 'RWAClient'):
        """
        Initialize networks endpoint

        Args:
            client: The main RWA client instance
        """
        self.client = client

    async def get_network(self, network_slug: str) -> Dict:
        """
        Get details for a specific network

        Args:
            network_slug: The slug identifier for the network

        Returns:
            Network details dictionary
        """
        endpoint = f"/_next/data/{self.client.build_id}/networks/{network_slug}.json"
        params = {"networkSlug": network_slug}
        return await self.client._request("GET", endpoint, params=params)

    async def list_networks(self) -> Dict:
        """
        List all available networks

        Returns:
            Dictionary containing all networks
        """
        endpoint = f"/_next/data/{self.client.build_id}/networks.json"
        return await self.client._request("GET", endpoint)