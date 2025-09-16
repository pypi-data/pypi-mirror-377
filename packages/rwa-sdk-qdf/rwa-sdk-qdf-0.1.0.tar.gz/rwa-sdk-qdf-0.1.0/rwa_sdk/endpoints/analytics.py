"""
RWA.xyz SDK Analytics Endpoint
Handle analytics and tracking operations
"""

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..client import RWAClient


class RWAAnalytics:
    """Handle analytics operations"""

    def __init__(self, client: 'RWAClient'):
        """
        Initialize analytics endpoint

        Args:
            client: The main RWA client instance
        """
        self.client = client

    async def track(self, event_name: str, properties: Dict) -> Dict:
        """
        Track an analytics event

        Args:
            event_name: Name of the event to track
            properties: Event properties dictionary

        Returns:
            Tracking response dictionary
        """
        endpoint = "/api/trpc/analytics.track"
        params = {"batch": "1"}
        data = {
            "0": {
                "name": event_name,
                "logRocketSessionUrl": "",
                "properties": properties
            }
        }
        return await self.client._request("POST", endpoint, params=params, json=data)