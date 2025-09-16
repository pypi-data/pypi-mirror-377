"""
RWA.xyz SDK Exceptions
Custom exceptions for the RWA.xyz SDK
"""

from typing import Any, Optional


class RWAError(Exception):
    """Base exception for all RWA SDK errors"""

    def __init__(self, message: str, details: Optional[Any] = None):
        """
        Initialize RWA error

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details


class RWAAuthError(RWAError):
    """Authentication related errors"""
    pass


class RWAAPIError(RWAError):
    """API related errors"""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Any] = None):
        """
        Initialize API error

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Response data from the API
        """
        super().__init__(message, response_data)
        self.status_code = status_code
        self.response_data = response_data


class RWANetworkError(RWAError):
    """Network related errors"""
    pass


class RWAValidationError(RWAError):
    """Validation related errors"""
    pass


class RWARateLimitError(RWAAPIError):
    """Rate limiting errors"""
    pass


class RWANotFoundError(RWAAPIError):
    """Resource not found errors"""
    pass


class RWAServerError(RWAAPIError):
    """Server-side errors"""
    pass