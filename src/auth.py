"""IOL Authentication module."""

import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from src.exceptions import InvalidCredentialsError, NetworkError, TokenExpiredError


class IOLAuth:
    """Handle IOL API authentication.

    This class manages login and token refresh operations.
    It does NOT store tokens in session state - that's the app's responsibility.
    """

    BASE_URL = "https://api.invertironline.com"
    TOKEN_ENDPOINT = "/token"  # Note: Auth uses /token, not /api/v2/token

    def __init__(self):
        self.token_data: Optional[Dict] = None

    def login(self, username: str, password: str) -> Dict:
        """
        Login to IOL API.

        Args:
            username: IOL username
            password: IOL password

        Returns:
            Token data dict with access_token, refresh_token, expires_at

        Raises:
            InvalidCredentialsError: If credentials are wrong
            NetworkError: If connection fails
        """
        payload = {
            "username": username,
            "password": password,
            "grant_type": "password",
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}{self.TOKEN_ENDPOINT}",
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
        except requests.exceptions.RequestException as e:
            raise NetworkError(e)

        if response.status_code == 401:
            raise InvalidCredentialsError()

        if response.status_code == 400:
            data = response.json()
            if data.get("error") == "invalid_grant":
                raise InvalidCredentialsError()

        response.raise_for_status()

        data = response.json()
        self.token_data = self._parse_token_response(data)
        return self.token_data

    def refresh_token(self, refresh_token: str) -> Dict:
        """
        Refresh expired token.

        Args:
            refresh_token: The refresh token from previous login

        Returns:
            New token data dict with access_token, refresh_token, expires_at

        Raises:
            TokenExpiredError: If refresh token is also expired
            NetworkError: If connection fails
        """
        payload = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}{self.TOKEN_ENDPOINT}",
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
        except requests.exceptions.RequestException as e:
            raise NetworkError(e)

        if response.status_code in (400, 401):
            raise TokenExpiredError()

        response.raise_for_status()

        data = response.json()
        self.token_data = self._parse_token_response(data)
        return self.token_data

    def is_token_valid(self, token_data: Dict) -> bool:
        """
        Check if token is still valid (not expired).

        Args:
            token_data: Dict containing expires_at datetime

        Returns:
            True if token is still valid, False otherwise
        """
        expires_at = token_data.get("expires_at")
        if not expires_at:
            return False

        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))

        now = datetime.now(timezone.utc)
        # Add 30 second buffer to avoid edge cases
        return expires_at > now + timedelta(seconds=30)

    def _parse_token_response(self, response_data: Dict) -> Dict:
        """
        Parse IOL response and add expires_at datetime.

        Args:
            response_data: Raw response from IOL token endpoint

        Returns:
            Parsed token data with expires_at datetime
        """
        expires_in = response_data.get("expires_in", 900)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        return {
            "access_token": response_data["access_token"],
            "refresh_token": response_data["refresh_token"],
            "expires_in": expires_in,
            "expires_at": expires_at.isoformat(),
        }
