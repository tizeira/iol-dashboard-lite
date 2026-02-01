"""Tests for IOL Authentication module."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import responses

from src.auth import IOLAuth
from src.exceptions import InvalidCredentialsError, NetworkError, TokenExpiredError


@pytest.fixture
def fixtures():
    """Load test fixtures."""
    fixtures_path = Path(__file__).parent / "fixtures" / "iol_responses.json"
    with open(fixtures_path) as f:
        return json.load(f)


@pytest.fixture
def auth():
    """Create IOLAuth instance."""
    return IOLAuth()


class TestLogin:
    """Tests for login functionality."""

    @responses.activate
    def test_login_success(self, auth, fixtures):
        """Test successful login returns token data."""
        responses.add(
            responses.POST,
            f"{auth.BASE_URL}{auth.TOKEN_ENDPOINT}",
            json=fixtures["login_success"],
            status=200,
        )

        result = auth.login("testuser", "testpass")

        assert "access_token" in result
        assert "refresh_token" in result
        assert "expires_at" in result
        assert result["access_token"] == fixtures["login_success"]["access_token"]
        assert result["refresh_token"] == fixtures["login_success"]["refresh_token"]

    @responses.activate
    def test_login_invalid_credentials_401(self, auth):
        """Test 401 response raises InvalidCredentialsError."""
        responses.add(
            responses.POST,
            f"{auth.BASE_URL}{auth.TOKEN_ENDPOINT}",
            json={"error": "invalid_grant"},
            status=401,
        )

        with pytest.raises(InvalidCredentialsError):
            auth.login("baduser", "badpass")

    @responses.activate
    def test_login_invalid_credentials_400(self, auth, fixtures):
        """Test 400 with invalid_grant raises InvalidCredentialsError."""
        responses.add(
            responses.POST,
            f"{auth.BASE_URL}{auth.TOKEN_ENDPOINT}",
            json=fixtures["login_invalid"],
            status=400,
        )

        with pytest.raises(InvalidCredentialsError):
            auth.login("baduser", "badpass")

    @responses.activate
    def test_login_network_error(self, auth):
        """Test network error raises NetworkError."""
        import requests as req

        responses.add(
            responses.POST,
            f"{auth.BASE_URL}{auth.TOKEN_ENDPOINT}",
            body=req.exceptions.ConnectionError("Connection failed"),
        )

        with pytest.raises(NetworkError):
            auth.login("testuser", "testpass")

    @responses.activate
    def test_login_stores_token_data(self, auth, fixtures):
        """Test login stores token data in instance."""
        responses.add(
            responses.POST,
            f"{auth.BASE_URL}{auth.TOKEN_ENDPOINT}",
            json=fixtures["login_success"],
            status=200,
        )

        auth.login("testuser", "testpass")

        assert auth.token_data is not None
        assert (
            auth.token_data["access_token"] == fixtures["login_success"]["access_token"]
        )


class TestRefreshToken:
    """Tests for token refresh functionality."""

    @responses.activate
    def test_refresh_token_success(self, auth, fixtures):
        """Test successful token refresh."""
        responses.add(
            responses.POST,
            f"{auth.BASE_URL}{auth.TOKEN_ENDPOINT}",
            json=fixtures["token_refresh_success"],
            status=200,
        )

        result = auth.refresh_token("old_refresh_token")

        assert "access_token" in result
        assert "refresh_token" in result
        assert (
            result["access_token"] == fixtures["token_refresh_success"]["access_token"]
        )

    @responses.activate
    def test_refresh_token_expired(self, auth):
        """Test expired refresh token raises TokenExpiredError."""
        responses.add(
            responses.POST,
            f"{auth.BASE_URL}{auth.TOKEN_ENDPOINT}",
            json={"error": "invalid_grant"},
            status=400,
        )

        with pytest.raises(TokenExpiredError):
            auth.refresh_token("expired_refresh_token")

    @responses.activate
    def test_refresh_token_401(self, auth):
        """Test 401 on refresh raises TokenExpiredError."""
        responses.add(
            responses.POST,
            f"{auth.BASE_URL}{auth.TOKEN_ENDPOINT}",
            json={"error": "invalid_token"},
            status=401,
        )

        with pytest.raises(TokenExpiredError):
            auth.refresh_token("invalid_refresh_token")


class TestTokenValidation:
    """Tests for token validation."""

    def test_token_valid(self, auth):
        """Test is_token_valid returns True for valid token."""
        token_data = {
            "access_token": "test_token",
            "expires_at": (
                datetime.now(timezone.utc) + timedelta(minutes=10)
            ).isoformat(),
        }

        assert auth.is_token_valid(token_data) is True

    def test_token_expired(self, auth):
        """Test is_token_valid returns False for expired token."""
        token_data = {
            "access_token": "test_token",
            "expires_at": (
                datetime.now(timezone.utc) - timedelta(minutes=10)
            ).isoformat(),
        }

        assert auth.is_token_valid(token_data) is False

    def test_token_about_to_expire(self, auth):
        """Test is_token_valid returns False for token expiring within 30s."""
        token_data = {
            "access_token": "test_token",
            "expires_at": (
                datetime.now(timezone.utc) + timedelta(seconds=20)
            ).isoformat(),
        }

        assert auth.is_token_valid(token_data) is False

    def test_token_no_expires_at(self, auth):
        """Test is_token_valid returns False when expires_at is missing."""
        token_data = {
            "access_token": "test_token",
        }

        assert auth.is_token_valid(token_data) is False

    def test_token_with_z_suffix(self, auth):
        """Test is_token_valid handles Z suffix in ISO datetime."""
        token_data = {
            "access_token": "test_token",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        }

        assert auth.is_token_valid(token_data) is True


class TestParseTokenResponse:
    """Tests for _parse_token_response."""

    def test_parse_adds_expires_at(self, auth, fixtures):
        """Test parsing adds expires_at datetime."""
        result = auth._parse_token_response(fixtures["login_success"])

        assert "expires_at" in result
        # expires_at should be a valid ISO datetime string
        expires_at = datetime.fromisoformat(result["expires_at"].replace("Z", "+00:00"))
        assert expires_at > datetime.now(timezone.utc)

    def test_parse_preserves_tokens(self, auth, fixtures):
        """Test parsing preserves access and refresh tokens."""
        result = auth._parse_token_response(fixtures["login_success"])

        assert result["access_token"] == fixtures["login_success"]["access_token"]
        assert result["refresh_token"] == fixtures["login_success"]["refresh_token"]

    def test_parse_default_expires_in(self, auth):
        """Test parsing uses default 900s when expires_in missing."""
        response_data = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
        }

        result = auth._parse_token_response(response_data)

        assert result["expires_in"] == 900
