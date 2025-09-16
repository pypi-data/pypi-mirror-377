"""
RWA.xyz SDK Authentication Module
Handles authentication for RWA.xyz API
"""

from typing import Dict, Optional


class RWAAuth:
    """Handle authentication for RWA.xyz API"""

    def __init__(self, email: Optional[str] = None, session_token: Optional[str] = None):
        """
        Initialize RWA authentication

        Args:
            email: User email for authentication
            session_token: Existing session token if available
        """
        self.email = email
        self.session_token = session_token
        self.cookies: Dict[str, str] = {}

    def set_session(self, session_token: str) -> None:
        """
        Set the session token for authentication

        Args:
            session_token: The session token to use for authentication
        """
        self.session_token = session_token
        self.cookies['__Secure-next-auth.session-token'] = session_token

    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests

        Returns:
            Dictionary of headers to include in requests
        """
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }
        return headers

    def is_authenticated(self) -> bool:
        """
        Check if the user is authenticated

        Returns:
            True if authenticated, False otherwise
        """
        return self.session_token is not None

    def clear_session(self) -> None:
        """Clear the current session"""
        self.session_token = None
        self.cookies.clear()