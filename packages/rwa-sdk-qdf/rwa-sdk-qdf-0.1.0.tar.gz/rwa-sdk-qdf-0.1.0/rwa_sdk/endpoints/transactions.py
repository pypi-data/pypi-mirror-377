"""
RWA.xyz SDK Transactions Endpoint
Handle transaction-related operations
"""

import json
from typing import TYPE_CHECKING, Dict, Optional

from ..models import SortDirection

if TYPE_CHECKING:
    from ..client import RWAClient


class RWATransactions:
    """Handle transaction-related operations"""

    def __init__(self, client: 'RWAClient'):
        """
        Initialize transactions endpoint

        Args:
            client: The main RWA client instance
        """
        self.client = client

    async def query(self,
                   asset_id: Optional[int] = None,
                   token_address: Optional[str] = None,
                   sort_field: str = "timestamp",
                   sort_direction: SortDirection = SortDirection.DESC,
                   page: int = 1,
                   per_page: int = 15) -> Dict:
        """
        Query transactions

        Args:
            asset_id: Filter by asset ID
            token_address: Filter by token address
            sort_field: Field to sort by
            sort_direction: Sort direction (ASC or DESC)
            page: Page number for pagination
            per_page: Number of results per page

        Returns:
            Transaction query results
        """
        filter_dict = {}
        if asset_id:
            filter_dict = {
                "operator": "equals",
                "field": "assetID",
                "value": asset_id
            }
        elif token_address:
            filter_dict = {
                "operator": "equals",
                "field": "tokenAddress",
                "value": token_address
            }

        query = {
            "query": {
                "filter": filter_dict,
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

        endpoint = "/api/trpc/transactions.query"
        params = {
            "batch": "1",
            "input": json.dumps({"0": query})
        }
        return await self.client._request("GET", endpoint, params=params)