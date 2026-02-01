"""Tests for IOL API Client module."""

import json
from pathlib import Path

import pytest
import responses

from src.api_client import IOLClient
from src.exceptions import (
    IOLAPIError,
    NetworkError,
    RateLimitError,
    TokenExpiredError,
)


@pytest.fixture
def fixtures():
    """Load test fixtures."""
    fixtures_path = Path(__file__).parent / "fixtures" / "iol_responses.json"
    with open(fixtures_path) as f:
        return json.load(f)


@pytest.fixture
def client():
    """Create IOLClient instance with test token."""
    return IOLClient("test_access_token")


class TestClientInit:
    """Tests for client initialization."""

    def test_init_sets_token(self, client):
        """Test client stores token."""
        assert client.token == "test_access_token"

    def test_init_sets_headers(self, client):
        """Test client sets authorization header."""
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test_access_token"


class TestCheckResponse:
    """Tests for _check_response method."""

    @responses.activate
    def test_401_raises_token_expired(self, client):
        """Test 401 response raises TokenExpiredError."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/portafolio/argentina",
            json={"error": "unauthorized"},
            status=401,
        )

        response = client.session.get(f"{client.BASE_URL}/api/v2/portafolio/argentina")

        with pytest.raises(TokenExpiredError):
            client._check_response(response)

    @responses.activate
    def test_429_raises_rate_limit(self, client):
        """Test 429 response raises RateLimitError."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/portafolio/argentina",
            json={"error": "rate_limit"},
            status=429,
            headers={"Retry-After": "120"},
        )

        response = client.session.get(f"{client.BASE_URL}/api/v2/portafolio/argentina")

        with pytest.raises(RateLimitError) as exc_info:
            client._check_response(response)

        assert exc_info.value.retry_after == 120

    @responses.activate
    def test_error_in_200_body_token_expired(self, client, fixtures):
        """Test error in 200 body with code 401 raises TokenExpiredError."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/portafolio/argentina",
            json=fixtures["error_in_200_body"],
            status=200,
        )

        response = client.session.get(f"{client.BASE_URL}/api/v2/portafolio/argentina")

        with pytest.raises(TokenExpiredError):
            client._check_response(response)

    @responses.activate
    def test_error_in_200_body_generic(self, client, fixtures):
        """Test generic error in 200 body raises IOLAPIError."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/portafolio/argentina",
            json=fixtures["generic_api_error"],
            status=200,
        )

        response = client.session.get(f"{client.BASE_URL}/api/v2/portafolio/argentina")

        with pytest.raises(IOLAPIError):
            client._check_response(response)

    @responses.activate
    def test_success_returns_data(self, client, fixtures):
        """Test successful response returns parsed JSON."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/portafolio/argentina",
            json=fixtures["portfolio_example"],
            status=200,
        )

        response = client.session.get(f"{client.BASE_URL}/api/v2/portafolio/argentina")
        data = client._check_response(response)

        assert "activos" in data
        assert data["totalEnPesos"] == fixtures["portfolio_example"]["totalEnPesos"]


class TestGetPortfolio:
    """Tests for get_portfolio method."""

    @responses.activate
    def test_get_portfolio_success(self, client, fixtures):
        """Test successful portfolio fetch and normalization."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/portafolio/argentina",
            json=fixtures["portfolio_example"],
            status=200,
        )

        result = client.get_portfolio()

        assert "activos" in result
        assert "total" in result
        assert "total_usd" in result
        assert result["total"] == fixtures["portfolio_example"]["totalEnPesos"]
        assert result["total_usd"] == fixtures["portfolio_example"]["totalEnDolares"]
        assert len(result["activos"]) == 2

    @responses.activate
    def test_get_portfolio_empty(self, client, fixtures):
        """Test empty portfolio handling."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/portafolio/argentina",
            json=fixtures["portfolio_empty"],
            status=200,
        )

        result = client.get_portfolio()

        assert result["activos"] == []
        assert result["total"] == 0
        assert result["total_usd"] == 0

    @responses.activate
    def test_get_portfolio_network_error(self, client):
        """Test network error raises NetworkError."""
        import requests as req

        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/portafolio/argentina",
            body=req.exceptions.ConnectionError("Connection failed"),
        )

        with pytest.raises(NetworkError):
            client.get_portfolio()


class TestGetQuotes:
    """Tests for get_quotes method."""

    @responses.activate
    def test_get_quotes_success(self, client, fixtures):
        """Test successful quotes fetch."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/Cotizaciones/acciones/argentina/Todos",
            json=fixtures["quotes_example"],
            status=200,
        )

        result = client.get_quotes()

        assert len(result) == 2
        assert result[0]["simbolo"] == "GGAL"
        assert result[1]["simbolo"] == "YPFD"

    @responses.activate
    def test_get_quotes_market_closed(self, client, fixtures):
        """Test quotes with null values (market closed)."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/Cotizaciones/acciones/argentina/Todos",
            json=fixtures["quotes_market_closed"],
            status=200,
        )

        result = client.get_quotes()

        assert len(result) == 1
        assert result[0]["variacion"] is None
        assert result[0]["puntas"] is None

    @responses.activate
    def test_get_quotes_different_instrument(self, client, fixtures):
        """Test quotes with different instrument type."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/Cotizaciones/cedears/argentina/Todos",
            json=fixtures["quotes_example"],
            status=200,
        )

        result = client.get_quotes(instrument="cedears")

        assert len(result) == 2

    @responses.activate
    def test_get_quotes_wrapped_response(self, client, fixtures):
        """Test quotes when response is wrapped in 'titulos' key."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/Cotizaciones/acciones/argentina/Todos",
            json={"titulos": fixtures["quotes_example"]},
            status=200,
        )

        result = client.get_quotes()

        assert len(result) == 2


class TestGetAccountStatus:
    """Tests for get_account_status method."""

    @responses.activate
    def test_get_account_status_success(self, client, fixtures):
        """Test successful account status fetch."""
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/estadocuenta",
            json=fixtures["account_status"],
            status=200,
        )

        result = client.get_account_status()

        assert "cuentas" in result
        assert len(result["cuentas"]) == 2
        assert result["cuentas"][0]["tipo"] == "PESOS"
        assert result["cuentas"][1]["tipo"] == "DOLARES"


class TestGetInstrumentDetail:
    """Tests for get_instrument_detail method."""

    @responses.activate
    def test_get_instrument_detail_success(self, client):
        """Test successful instrument detail fetch."""
        mock_response = {
            "simbolo": "GGAL",
            "descripcion": "Grupo Financiero Galicia S.A.",
            "mercado": "BCBA",
        }
        responses.add(
            responses.GET,
            f"{client.BASE_URL}/api/v2/bCBA/Titulos/GGAL",
            json=mock_response,
            status=200,
        )

        result = client.get_instrument_detail("GGAL")

        assert result["simbolo"] == "GGAL"
        assert result["mercado"] == "BCBA"
