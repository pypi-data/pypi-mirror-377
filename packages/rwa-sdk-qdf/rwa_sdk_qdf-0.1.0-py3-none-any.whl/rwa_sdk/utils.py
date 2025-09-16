"""
RWA.xyz SDK Utilities
Helper functions for data processing
"""

import base64
import json
import zlib
from typing import Any, Dict, Optional


def try_decompress_response(data: Any) -> Any:
    """
    Try to decompress API response data if it appears to be compressed.

    Args:
        data: The response data (could be dict, list, or string)

    Returns:
        Decompressed data if successful, otherwise original data

    Note:
        The RWA.xyz API sometimes returns compressed data in Next.js format.
        This is a proprietary compression format that may require reverse
        engineering or official API documentation to properly decode.
    """
    # If data is already a dict or list, return as-is
    if isinstance(data, (dict, list)) and not isinstance(data, str):
        return data

    # If it's a string that looks like compressed data
    if isinstance(data, str) and len(data) > 100:
        # Check if it might be base64 encoded compressed data
        if all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in data[:100]):
            try:
                # Try standard base64 + zlib decompression
                decoded = base64.b64decode(data)
                decompressed = zlib.decompress(decoded)
                result = json.loads(decompressed.decode('utf-8'))
                return result
            except:
                pass

            try:
                # Try with padding
                padded = data + '=' * (4 - len(data) % 4)
                decoded = base64.b64decode(padded)
                decompressed = zlib.decompress(decoded)
                result = json.loads(decompressed.decode('utf-8'))
                return result
            except:
                pass

    # Return original data if decompression fails
    return data


def extract_readable_data(response: Dict) -> Dict:
    """
    Extract readable data from API responses.

    Some endpoints return compressed or encoded data that requires
    special handling. This function attempts to extract any readable
    data from the response.

    Args:
        response: The API response dictionary

    Returns:
        Dictionary with extracted readable data
    """
    readable = {}

    # Check for pageProps (Next.js data)
    if isinstance(response, dict):
        if 'pageProps' in response:
            page_props = response['pageProps']

            # Check for redirects
            if '__N_REDIRECT' in page_props:
                readable['redirect'] = page_props['__N_REDIRECT']
                readable['redirect_status'] = page_props.get('__N_REDIRECT_STATUS', 308)

            # Extract other readable fields
            for key, value in page_props.items():
                if not key.startswith('__'):
                    readable[key] = value

        # Check for result data
        if 'result' in response:
            result = response['result']
            if isinstance(result, dict) and 'data' in result:
                # If data is compressed string, note it
                if isinstance(result['data'], str) and len(result['data']) > 100:
                    readable['data_status'] = 'compressed'
                    readable['data_length'] = len(result['data'])
                else:
                    readable['data'] = result['data']

    return readable if readable else response


def format_currency(value: float, currency: str = 'USD') -> str:
    """
    Format a number as currency.

    Args:
        value: The numeric value
        currency: Currency code (default: USD)

    Returns:
        Formatted currency string
    """
    if currency == 'USD':
        return f"${value:,.2f}"
    else:
        return f"{value:,.2f} {currency}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format a number as percentage.

    Args:
        value: The decimal value (0.05 = 5%)
        decimal_places: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"