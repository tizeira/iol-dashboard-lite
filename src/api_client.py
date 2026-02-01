"""IOL API Client module."""

import requests
from typing import Dict, List

from src.exceptions import (
    IOLAPIError,
    TokenExpiredError,
    RateLimitError,
    NetworkError,
)


class IOLClient:
    """HTTP client for IOL API.

    This class handles all API requests to IOL.
    It does NOT cache responses - caching is handled in the UI layer.
    """

    BASE_URL = "https://api.invertironline.com"
    TIMEOUT = 10  # seconds

    def __init__(self, token: str):
        """
        Initialize client with access token.

        Args:
            token: Valid IOL access token
        """
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            NetworkError: If connection fails
        """
        kwargs.setdefault("timeout", self.TIMEOUT)

        try:
            response = self.session.request(
                method,
                f"{self.BASE_URL}{endpoint}",
                **kwargs,
            )
            return response
        except requests.exceptions.RequestException as e:
            raise NetworkError(e)

    def _check_response(self, response: requests.Response) -> Dict:
        """
        Check response for errors.

        CRITICAL: IOL sometimes returns 200 with error in body:
        {"error": "...", "code": 401}

        Args:
            response: Response object to check

        Returns:
            Parsed JSON data

        Raises:
            TokenExpiredError: If token is expired
            RateLimitError: If rate limit is hit
            IOLAPIError: For other API errors
        """
        if response.status_code == 401:
            raise TokenExpiredError()

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(retry_after)

        response.raise_for_status()

        data = response.json()

        # Error disguised as success (IOL quirk)
        if "error" in data:
            error_code = data.get("code")
            if error_code == 401:
                raise TokenExpiredError()
            raise IOLAPIError(data.get("message", data["error"]))

        return data

    def get_portfolio(self, country: str = "argentina") -> Dict:
        """
        Fetch portfolio data.

        Args:
            country: Country code (default: argentina)

        Returns:
            Normalized dict with keys: activos, total, total_usd
        """
        response = self._request("GET", f"/api/v2/portafolio/{country}")
        data = self._check_response(response)

        # Normalize structure for UI
        return {
            "activos": data.get("activos", []),
            "total": data.get("totalEnPesos", 0),
            "total_usd": data.get("totalEnDolares", 0),
        }

    def get_quotes(
        self, instrument: str = "acciones", country: str = "argentina"
    ) -> List[Dict]:
        """
        Fetch market quotes.

        Args:
            instrument: Instrument type (acciones, bonos, cedears, etc.)
            country: Country code (default: argentina)

        Returns:
            List of quote dicts with symbol, price, variation, etc.
        """
        response = self._request(
            "GET",
            f"/api/v2/Cotizaciones/{instrument}/{country}/Todos",
        )
        data = self._check_response(response)

        # Response is a list directly
        if isinstance(data, list):
            return data

        # Some endpoints wrap in 'titulos' key
        return data.get("titulos", [])

    def get_account_status(self) -> Dict:
        """
        Fetch account balance.

        Returns:
            Dict with account balances by currency
        """
        response = self._request("GET", "/api/v2/estadocuenta")
        data = self._check_response(response)

        return {
            "cuentas": data.get("cuentas", []),
        }

    def get_instrument_detail(self, symbol: str, market: str = "bCBA") -> Dict:
        """
        Fetch detailed info for a specific instrument.

        Args:
            symbol: Instrument symbol (e.g., GGAL)
            market: Market code (default: bCBA)

        Returns:
            Dict with instrument details
        """
        response = self._request("GET", f"/api/v2/{market}/Titulos/{symbol}")
        return self._check_response(response)
