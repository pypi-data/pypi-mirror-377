"""
RWA.xyz SDK Assets Endpoint
Handle asset-related operations
"""

import json
from typing import TYPE_CHECKING, Dict

from ..models import (
    AssetClass,
    AggregateFunction,
    CompositeFilter,
    Filter,
    FilterOperator,
    MeasureID,
    Pagination,
    Sort,
    SortDirection,
    SortField,
    TimeseriesQuery,
    Aggregate,
)

if TYPE_CHECKING:
    from ..client import RWAClient


class RWAAssets:
    """Handle asset-related operations"""

    def __init__(self, client: 'RWAClient'):
        """
        Initialize assets endpoint

        Args:
            client: The main RWA client instance
        """
        self.client = client

    async def get_asset(self, asset_slug: str) -> Dict:
        """
        Get details for a specific asset

        Args:
            asset_slug: The slug identifier for the asset

        Returns:
            Asset details dictionary
        """
        endpoint = f"/_next/data/{self.client.build_id}/assets/{asset_slug}.json"
        params = {"assetSlug": asset_slug}
        return await self.client._request("GET", endpoint, params=params)

    async def get_timeseries(self, query: TimeseriesQuery) -> Dict:
        """
        Get timeseries data for assets

        Args:
            query: The timeseries query configuration

        Returns:
            Timeseries data dictionary
        """
        endpoint = "/api/trpc/assetTimeseries.queryTimeseries"
        params = {
            "batch": "1",
            "input": json.dumps({"0": {"query": query.to_dict()}})
        }
        return await self.client._request("GET", endpoint, params=params)

    async def get_stablecoins_overview(self) -> Dict:
        """
        Get stablecoins market overview

        Returns:
            Stablecoins market overview data
        """
        query = TimeseriesQuery(
            filter=CompositeFilter(
                operator=FilterOperator.AND,
                filters=[
                    Filter("measureID", FilterOperator.EQUALS, MeasureID.MARKET_CAP.value),
                    Filter("assetClassID", FilterOperator.EQUALS, AssetClass.STABLECOINS.value)
                ]
            ),
            sort=Sort(SortField.DATE, SortDirection.ASC),
            pagination=Pagination(1, 25),
            aggregate=Aggregate("asset", AggregateFunction.SUM, "day")
        )
        return await self.get_timeseries(query)

    async def get_treasuries_overview(self) -> Dict:
        """
        Get treasuries market overview

        Returns:
            Treasuries market overview data
        """
        query = TimeseriesQuery(
            filter=CompositeFilter(
                operator=FilterOperator.AND,
                filters=[
                    Filter("assetClassID", FilterOperator.EQUALS, AssetClass.TREASURIES.value),
                    Filter("date", FilterOperator.ON_OR_AFTER, "2023-01-01T05:00:00.000Z"),
                    Filter("isInvestable", FilterOperator.EQUALS, True),
                    Filter("measureID", FilterOperator.EQUALS, MeasureID.TOTAL_VALUE_LOCKED.value)
                ]
            ),
            sort=Sort(SortField.DATE, SortDirection.ASC),
            pagination=Pagination(1, 25),
            aggregate=Aggregate("asset", AggregateFunction.SUM, "day")
        )
        return await self.get_timeseries(query)