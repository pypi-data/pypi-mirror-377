"""
RWA.xyz SDK Token Holders Endpoint
Handle token holder operations
"""

import json
from typing import TYPE_CHECKING, Dict

from ..models import SortDirection

if TYPE_CHECKING:
    from ..client import RWAClient


class RWATokenHolders:
    """Handle token holder operations"""

    def __init__(self, client: 'RWAClient'):
        """
        Initialize token holders endpoint

        Args:
            client: The main RWA client instance
        """
        self.client = client

    async def query(self,
                   token_id: int,
                   sort_field: str = "holdingTokenValueUSD",
                   sort_direction: SortDirection = SortDirection.DESC,
                   page: int = 1,
                   per_page: int = 1500) -> Dict:
        """
        Query token holders

        Args:
            token_id: The token ID to query holders for
            sort_field: Field to sort by
            sort_direction: Sort direction (ASC or DESC)
            page: Page number for pagination
            per_page: Number of results per page

        Returns:
            Token holders query results
        """
        query = {
            "query": {
                "filter": {
                    "operator": "or",
                    "filters": [{
                        "operator": "equals",
                        "value": token_id,
                        "field": "tokenID"
                    }]
                },
                "sort": {
                    "direction": sort_direction.value,
                    "field": sort_field
                },
                "pagination": {
                    "page": page,
                    "perPage": per_page
                }
            }
        }

        endpoint = "/api/trpc/tokenHolders.query"
        params = {
            "batch": "1",
            "input": json.dumps({"0": query})
        }
        return await self.client._request("GET", endpoint, params=params)