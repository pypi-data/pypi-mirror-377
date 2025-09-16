"""
RWA.xyz SDK Models
Contains enums, data classes, and type definitions
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


# Enums and Constants
class AssetClass(Enum):
    """Asset class categories supported by RWA.xyz"""
    STABLECOINS = 28
    TREASURIES = 27
    GLOBAL_BONDS = "global-bonds"
    PRIVATE_CREDIT = "private-credit"
    COMMODITIES = "commodities"
    INSTITUTIONAL_FUNDS = "institutional-funds"
    STOCKS = "stocks"


class Network(Enum):
    """Blockchain networks supported by RWA.xyz"""
    ETHEREUM = "ethereum"
    TRON = "tron"
    SOLANA = "solana"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    BASE = "base"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"
    BNB_CHAIN = "bnb-chain"
    ZKSYNC_ERA = "zksync-era"
    XRP_LEDGER = "xrp-ledger"
    NEAR = "near"
    STELLAR = "stellar"
    MANTLE = "mantle"
    MANTA_PACIFIC = "manta-pacific"
    BLAST = "blast"
    PLUME = "plume"
    XDC = "xdc"


class SortDirection(Enum):
    """Sort direction options"""
    ASC = "asc"
    DESC = "desc"


class SortField(Enum):
    """Available sort fields"""
    DATE = "date"
    TIMESTAMP = "timestamp"
    CREATED_TIME = "createdTime"
    MODIFIED_TIME = "modifiedTime"
    NAME = "name"
    VALUE_USD = "holdingTokenValueUSD"


class MeasureID(Enum):
    """Available measure IDs for analytics"""
    MARKET_CAP = 70
    TOTAL_VALUE_LOCKED = 71
    SUPPLY = 72
    VOLUME = 73


class AggregateFunction(Enum):
    """Available aggregate functions"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"


class FilterOperator(Enum):
    """Available filter operators"""
    EQUALS = "equals"
    NOT_EQUALS = "notEquals"
    GREATER_THAN = "greaterThan"
    LESS_THAN = "lessThan"
    IN = "in"
    NOT_IN = "notIn"
    AND = "and"
    OR = "or"
    ON_OR_AFTER = "onOrAfter"
    ON_OR_BEFORE = "onOrBefore"


# Data Classes
@dataclass
class Pagination:
    """Pagination parameters for API requests"""
    page: int = 1
    per_page: int = 25

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary format for API requests"""
        return {"page": self.page, "perPage": self.per_page}


@dataclass
class Sort:
    """Sort parameters for API requests"""
    field: Union[str, SortField]
    direction: SortDirection = SortDirection.DESC

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API requests"""
        field_value = self.field.value if isinstance(self.field, SortField) else self.field
        return {
            "field": field_value,
            "direction": self.direction.value
        }


@dataclass
class Filter:
    """Filter parameters for API requests"""
    field: str
    operator: FilterOperator
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API requests"""
        return {
            "field": self.field,
            "operator": self.operator.value,
            "value": self.value
        }


@dataclass
class CompositeFilter:
    """Composite filter for combining multiple filters"""
    operator: FilterOperator
    filters: List[Union[Filter, 'CompositeFilter']]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API requests"""
        return {
            "operator": self.operator.value,
            "filters": [f.to_dict() for f in self.filters]
        }


@dataclass
class Aggregate:
    """Aggregation parameters for API requests"""
    group_by: str = "asset"
    aggregate_function: AggregateFunction = AggregateFunction.SUM
    interval: str = "day"

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API requests"""
        return {
            "groupBy": self.group_by,
            "aggregateFunction": self.aggregate_function.value,
            "interval": self.interval
        }


@dataclass
class TimeseriesQuery:
    """Complete timeseries query with all parameters"""
    filter: Union[Filter, CompositeFilter]
    sort: Optional[Sort] = None
    pagination: Optional[Pagination] = None
    aggregate: Optional[Aggregate] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API requests"""
        result = {"filter": self.filter.to_dict()}
        if self.sort:
            result["sort"] = self.sort.to_dict()
        if self.pagination:
            result["pagination"] = self.pagination.to_dict()
        if self.aggregate:
            result["aggregate"] = self.aggregate.to_dict()
        return result