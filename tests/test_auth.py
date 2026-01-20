"""Tests for twitch-client authentication."""

import pytest
from twitch_client import TwitchAuth, TwitchCredentials, TwitchHTTPClient


class TestCredentials:
    """Test TwitchCredentials loading."""

    def test_credentials_from_env(self, monkeypatch):
        """Test loading credentials from environment variables."""
        monkeypatch.setenv("TWITCH_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("TWITCH_CLIENT_SECRET", "test_secret")
        monkeypatch.setenv("TWITCH_ACCESS_TOKEN", "test_token")
        monkeypatch.setenv("TWITCH_REFRESH_TOKEN", "test_refresh")

        creds = TwitchCredentials()
        assert creds.client_id == "test_client_id"
        assert creds.client_secret == "test_secret"
        assert creds.access_token == "test_token"
        assert creds.refresh_token == "test_refresh"


class TestAuth:
    """Test TwitchAuth token management."""

    @pytest.fixture
    def mock_credentials(self, monkeypatch):
        """Set up mock credentials."""
        monkeypatch.setenv("TWITCH_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("TWITCH_CLIENT_SECRET", "test_secret")
        monkeypatch.setenv("TWITCH_ACCESS_TOKEN", "test_token")
        monkeypatch.setenv("TWITCH_REFRESH_TOKEN", "test_refresh")
        return TwitchCredentials()

    def test_auth_init(self, mock_credentials):
        """Test TwitchAuth initialization."""
        auth = TwitchAuth(mock_credentials)
        assert auth.client_id == "test_client_id"


class TestHTTPClient:
    """Test TwitchHTTPClient."""

    @pytest.fixture
    def mock_credentials(self, monkeypatch):
        """Set up mock credentials."""
        monkeypatch.setenv("TWITCH_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("TWITCH_CLIENT_SECRET", "test_secret")
        monkeypatch.setenv("TWITCH_ACCESS_TOKEN", "test_token")
        monkeypatch.setenv("TWITCH_REFRESH_TOKEN", "test_refresh")
        return TwitchCredentials()

    def test_client_init(self, mock_credentials):
        """Test HTTP client initialization."""
        client = TwitchHTTPClient(credentials=mock_credentials)
        assert client.auth.client_id == "test_client_id"
