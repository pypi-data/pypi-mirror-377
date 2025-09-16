"""
RWA.xyz Python SDK
A comprehensive SDK for interacting with the RWA.xyz platform API
"""

from .client import RWAClient, RWAClientSync
from .auth import RWAAuth
from .models import (
    AssetClass,
    Network,
    SortDirection,
    SortField,
    MeasureID,
    AggregateFunction,
    FilterOperator,
    Pagination,
    Sort,
    Filter,
    CompositeFilter,
    Aggregate,
    TimeseriesQuery,
)
from .exceptions import (
    RWAError,
    RWAAuthError,
    RWAAPIError,
    RWANetworkError,
    RWAValidationError,
)

__version__ = "0.1.0"
__author__ = "RWA SDK Contributors"
__description__ = "Python SDK for interacting with the RWA.xyz platform API for tokenized real-world assets data"

__all__ = [
    # Main client classes
    "RWAClient",
    "RWAClientSync",
    "RWAAuth",

    # Models and enums
    "AssetClass",
    "Network",
    "SortDirection",
    "SortField",
    "MeasureID",
    "AggregateFunction",
    "FilterOperator",
    "Pagination",
    "Sort",
    "Filter",
    "CompositeFilter",
    "Aggregate",
    "TimeseriesQuery",

    # Exceptions
    "RWAError",
    "RWAAuthError",
    "RWAAPIError",
    "RWANetworkError",
    "RWAValidationError",
]