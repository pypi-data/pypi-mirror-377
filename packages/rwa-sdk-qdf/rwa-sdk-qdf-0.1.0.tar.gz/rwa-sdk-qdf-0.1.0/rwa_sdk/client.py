"""
RWA.xyz SDK Client
Main client classes for interacting with the RWA.xyz API
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
import aiohttp
import requests

from .auth import RWAAuth
from .endpoints.assets import RWAAssets
from .endpoints.transactions import RWATransactions
from .endpoints.token_holders import RWATokenHolders
from .endpoints.platforms import RWAPlatforms
from .endpoints.networks import RWANetworks
from .endpoints.users import RWAUsers
from .endpoints.search import RWASearch
from .endpoints.analytics import RWAAnalytics
from .exceptions import RWAAPIError, RWANetworkError
from .models import Network


class RWAClient:
    """Main async client for RWA.xyz API"""

    def __init__(
        self,
        base_url: str = "https://app.rwa.xyz",
        auth: Optional[RWAAuth] = None,
        build_id: str = "51twaOzJ6WEciC7TAayi1"
    ):
        """
        Initialize RWA API client

        Args:
            base_url: Base URL for RWA.xyz API
            auth: Authentication handler
            build_id: Build ID for Next.js data endpoints
        """
        self.base_url = base_url
        self.auth = auth or RWAAuth()
        self.build_id = build_id
        self.session = None

        # Initialize sub-clients
        self.assets = RWAAssets(self)
        self.transactions = RWATransactions(self)
        self.token_holders = RWATokenHolders(self)
        self.platforms = RWAPlatforms(self)
        self.networks = RWANetworks(self)
        self.users = RWAUsers(self)
        self.search = RWASearch(self)
        self.analytics = RWAAnalytics(self)

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(cookies=self.auth.cookies)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        data: Optional[Any] = None
    ) -> Dict:
        """
        Make an HTTP request to the API

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json: JSON body
            data: Request data

        Returns:
            Response data as dictionary

        Raises:
            RWAAPIError: For API errors
            RWANetworkError: For network errors
        """
        if not self.session:
            self.session = aiohttp.ClientSession(cookies=self.auth.cookies)

        url = f"{self.base_url}{endpoint}"
        headers = self.auth.get_headers()

        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                data=data
            ) as response:
                response_data = await response.json()

                if response.status >= 400:
                    raise RWAAPIError(
                        f"API request failed: {response.status}",
                        status_code=response.status,
                        response_data=response_data
                    )

                return response_data
        except aiohttp.ClientError as e:
            raise RWANetworkError(f"Network request failed: {str(e)}")

    def _sync_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        data: Optional[Any] = None
    ) -> Dict:
        """
        Make a synchronous HTTP request

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json: JSON body
            data: Request data

        Returns:
            Response data as dictionary

        Raises:
            RWAAPIError: For API errors
            RWANetworkError: For network errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.auth.get_headers()

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                data=data,
                cookies=self.auth.cookies
            )

            if response.status_code >= 400:
                raise RWAAPIError(
                    f"API request failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )

            return response.json()
        except requests.RequestException as e:
            raise RWANetworkError(f"Network request failed: {str(e)}")

    # Convenience methods for common queries
    async def get_stablecoin(self, symbol: str) -> Dict:
        """Get a specific stablecoin by symbol"""
        return await self.assets.get_asset(symbol)

    async def get_top_stablecoins(self, limit: int = 10) -> List[Dict]:
        """Get top stablecoins by market cap"""
        data = await self.assets.get_stablecoins_overview()
        # Parse and return top N stablecoins
        return data

    async def get_platform_assets(self, platform: str) -> Dict:
        """Get all assets for a specific platform"""
        return await self.platforms.get_platform(platform)

    async def get_network_activity(self, network: Network) -> Dict:
        """Get activity for a specific network"""
        return await self.networks.get_network(network.value)


class RWAClientSync:
    """Synchronous version of the RWA client"""

    def __init__(
        self,
        base_url: str = "https://app.rwa.xyz",
        auth: Optional[RWAAuth] = None,
        build_id: str = "51twaOzJ6WEciC7TAayi1"
    ):
        """
        Initialize synchronous RWA API client

        Args:
            base_url: Base URL for RWA.xyz API
            auth: Authentication handler
            build_id: Build ID for Next.js data endpoints
        """
        self.async_client = RWAClient(base_url, auth, build_id)

    def _run_async(self, coro):
        """Run an async coroutine synchronously"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # Fallback to creating a new event loop
            return asyncio.run(coro)

    def get_stablecoin(self, symbol: str) -> Dict:
        """Get a specific stablecoin by symbol"""
        return self._run_async(self.async_client.get_stablecoin(symbol))

    def get_stablecoins_overview(self) -> Dict:
        """Get stablecoins market overview"""
        return self._run_async(self.async_client.assets.get_stablecoins_overview())

    def get_treasuries_overview(self) -> Dict:
        """Get treasuries market overview"""
        return self._run_async(self.async_client.assets.get_treasuries_overview())

    def get_transactions(self, token_address: str, limit: int = 15) -> Dict:
        """Get transactions for a token"""
        return self._run_async(
            self.async_client.transactions.query(
                token_address=token_address,
                per_page=limit
            )
        )

    def get_platform(self, platform_slug: str) -> Dict:
        """Get platform details"""
        return self._run_async(self.async_client.platforms.get_platform(platform_slug))

    def get_network(self, network_slug: str) -> Dict:
        """Get network details"""
        return self._run_async(self.async_client.networks.get_network(network_slug))

    def get_token_holders(self, token_id: int, limit: int = 100) -> Dict:
        """Get token holders"""
        return self._run_async(
            self.async_client.token_holders.query(
                token_id=token_id,
                per_page=limit
            )
        )