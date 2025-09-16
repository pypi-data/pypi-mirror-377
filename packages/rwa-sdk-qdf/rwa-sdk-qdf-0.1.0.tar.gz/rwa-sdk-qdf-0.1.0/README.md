# RWA SDK QDF - by QuantDeFi.ai

🚀 **Professional Python SDK for Real-World Asset Data Analysis**

Access comprehensive tokenized asset data from RWA.xyz platform through QuantDeFi.ai's optimized SDK. Track $297B+ in global assets including stablecoins, tokenized treasuries, and real-world assets across 26+ blockchain networks.

**Built by [QuantDeFi.ai](https://quantdefi.ai) - Advanced Quantitative DeFi Analytics**

## Features

- **Async and Sync Support**: Both asynchronous and synchronous client implementations
- **Complete API Coverage**: Access to all RWA.xyz API endpoints
- **Type Safety**: Full type hints for better IDE support
- **Easy to Use**: Simple, intuitive API design
- **Comprehensive Data Models**: Well-structured data models for all API responses

## Installation

### From PyPI
```bash
pip install rwa-sdk-qdf
```

### From Source
```bash
git clone https://github.com/quantdefi/rwa-sdk-qdf.git
cd rwa-sdk-qdf
pip install -e .
```

## Quick Start

### Synchronous Usage

```python
from rwa_sdk import RWAClientSync

# Initialize the client
client = RWAClientSync()

# Get USDT stablecoin data
usdt = client.get_stablecoin("USDT")
print(f"USDT Market Cap: ${usdt['marketCap']:,.2f}")

# Get stablecoins overview
stables = client.get_stablecoins_overview()
print(f"Total Stablecoin Market: ${stables['total']:,.2f}")

# Get treasuries overview
treasuries = client.get_treasuries_overview()
print(f"Total Tokenized Treasuries: ${treasuries['total']:,.2f}")
```

### Asynchronous Usage

```python
import asyncio
from rwa_sdk import RWAClient, RWAAuth

async def main():
    # Initialize with authentication (optional)
    auth = RWAAuth(email="user@example.com")

    async with RWAClient(auth=auth) as client:
        # Get USDC details
        usdc = await client.get_stablecoin("USDC")
        print(f"USDC Data: {usdc}")

        # Get stablecoins overview
        stables = await client.assets.get_stablecoins_overview()
        print(f"Stablecoins Overview: {stables}")

        # Get transactions for a specific token
        txns = await client.transactions.query(
            token_address="0x45804880de22913dafe09f4980848ece6ecbaf78",
            per_page=5
        )
        print(f"Recent Transactions: {txns}")

# Run the async example
asyncio.run(main())
```

## API Modules

### Assets
Access asset-related data including stablecoins, treasuries, and other tokenized assets.

```python
# Get specific asset
asset = await client.assets.get_asset("USDT")

# Get timeseries data with custom query
from rwa_sdk import TimeseriesQuery, Filter, FilterOperator, MeasureID

query = TimeseriesQuery(
    filter=Filter("measureID", FilterOperator.EQUALS, MeasureID.MARKET_CAP.value)
)
data = await client.assets.get_timeseries(query)
```

### Transactions
Query blockchain transactions for tokens.

```python
# Get transactions for a token
transactions = await client.transactions.query(
    token_address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    per_page=10
)
```

### Token Holders
Get information about token holders.

```python
# Get top holders for a token
holders = await client.token_holders.query(
    token_id=123,
    per_page=100
)
```

### Platforms
Access platform-specific data.

```python
# Get platform details
platform = await client.platforms.get_platform("tether-holdings")

# List all platforms
platforms = await client.platforms.list_platforms()
```

### Networks
Get blockchain network information.

```python
# Get network details
from rwa_sdk import Network

ethereum = await client.networks.get_network(Network.ETHEREUM.value)

# List all networks
networks = await client.networks.list_networks()
```

## Data Models

The SDK provides comprehensive data models for working with the API:

- **AssetClass**: Enum for asset categories (STABLECOINS, TREASURIES, etc.)
- **Network**: Enum for blockchain networks
- **Filter/CompositeFilter**: Build complex queries
- **Sort**: Define sorting parameters
- **Pagination**: Control result pagination
- **TimeseriesQuery**: Create timeseries queries

## Advanced Usage

### Custom Queries

```python
from rwa_sdk import (
    TimeseriesQuery,
    CompositeFilter,
    Filter,
    FilterOperator,
    Sort,
    SortField,
    SortDirection,
    Pagination,
    Aggregate,
    AggregateFunction
)

# Build a complex query
query = TimeseriesQuery(
    filter=CompositeFilter(
        operator=FilterOperator.AND,
        filters=[
            Filter("assetClassID", FilterOperator.EQUALS, 28),
            Filter("date", FilterOperator.ON_OR_AFTER, "2023-01-01"),
            Filter("isInvestable", FilterOperator.EQUALS, True)
        ]
    ),
    sort=Sort(SortField.DATE, SortDirection.DESC),
    pagination=Pagination(page=1, per_page=50),
    aggregate=Aggregate(
        group_by="asset",
        aggregate_function=AggregateFunction.SUM,
        interval="day"
    )
)

result = await client.assets.get_timeseries(query)
```

### Error Handling

```python
from rwa_sdk import RWAAPIError, RWANetworkError

try:
    asset = await client.assets.get_asset("USDT")
except RWAAPIError as e:
    print(f"API error: {e.message}, Status: {e.status_code}")
except RWANetworkError as e:
    print(f"Network error: {e.message}")
```

## Authentication

Some endpoints require authentication. You can provide authentication credentials:

```python
from rwa_sdk import RWAAuth

# With email
auth = RWAAuth(email="user@example.com")

# With session token
auth = RWAAuth(session_token="your-session-token")

# Set session later
auth.set_session("new-session-token")

client = RWAClient(auth=auth)
```

## Known Limitations

### Compressed Data Responses

Some API endpoints return compressed data in a proprietary Next.js format. These responses appear as base64-like encoded strings. The SDK currently returns this data as-is. For most use cases, we recommend using endpoints that return standard JSON data, such as:

- Platform listings and details
- Direct asset queries
- Network information

If you encounter compressed data and need to access it, consider:
1. Using alternative endpoints that provide uncompressed data
2. Checking the RWA.xyz official documentation for data format specifications
3. Using the web interface at https://app.rwa.xyz for visual data access

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository or contact support@rwa.xyz

## Disclaimer

This SDK is provided as-is. Please ensure you comply with RWA.xyz's terms of service when using this SDK.