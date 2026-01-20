"""Twitch OAuth token management."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

import httpx
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import TwitchAuthError, TwitchTokenRefreshError


class TwitchCredentials(BaseSettings):
    """Twitch API credentials loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=os.getenv("TWITCH_ENV_FILE", "~/.twitch-secrets/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    client_id: str = Field(alias="TWITCH_CLIENT_ID")
    client_secret: str = Field(alias="TWITCH_CLIENT_SECRET")
    access_token: str = Field(alias="TWITCH_ACCESS_TOKEN")
    refresh_token: str = Field(alias="TWITCH_REFRESH_TOKEN")
    bot_username: str | None = Field(default=None, alias="TWITCH_BOT_USERNAME")
    channel: str | None = Field(default=None, alias="TWITCH_CHANNEL")


class TokenInfo(BaseModel):
    """Access token with metadata."""

    access_token: str
    refresh_token: str
    expires_at: datetime | None = None
    scopes: list[str] = Field(default_factory=list)


class TwitchAuth:
    """Manages Twitch OAuth tokens with automatic refresh."""

    TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    VALIDATE_URL = "https://id.twitch.tv/oauth2/validate"

    def __init__(
        self,
        credentials: TwitchCredentials | None = None,
        on_token_refresh: Callable[[TokenInfo], None] | None = None,
    ):
        """Initialize auth manager.

        Args:
            credentials: Twitch credentials. If None, loads from environment.
            on_token_refresh: Callback invoked when token is refreshed.
        """
        self.credentials = credentials or TwitchCredentials()
        self.on_token_refresh = on_token_refresh
        self._token_info: TokenInfo | None = None
        self._http_client: httpx.AsyncClient | None = None

    @property
    def client_id(self) -> str:
        """Get the client ID."""
        return self.credentials.client_id

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for auth requests."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def get_token(self) -> str:
        """Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token string.

        Raises:
            TwitchAuthError: If token cannot be obtained.
        """
        if self._token_info is None:
            # Initialize from credentials
            self._token_info = TokenInfo(
                access_token=self.credentials.access_token,
                refresh_token=self.credentials.refresh_token,
            )
            # Validate and get expiration info
            await self._validate_token()

        # Check if token is expired or about to expire (within 5 minutes)
        if self._token_info.expires_at:
            if datetime.utcnow() >= self._token_info.expires_at - timedelta(minutes=5):
                await self.refresh_token()

        return self._token_info.access_token

    async def _validate_token(self) -> None:
        """Validate the current token and update expiration info."""
        client = await self._get_http_client()
        response = await client.get(
            self.VALIDATE_URL,
            headers={"Authorization": f"OAuth {self._token_info.access_token}"},
        )

        if response.status_code == 401:
            # Token is invalid, try to refresh
            await self.refresh_token()
            return

        if response.status_code != 200:
            raise TwitchAuthError(f"Failed to validate token: {response.text}")

        data = response.json()
        expires_in = data.get("expires_in", 0)
        self._token_info.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        self._token_info.scopes = data.get("scopes", [])

    async def refresh_token(self) -> TokenInfo:
        """Refresh the access token using the refresh token.

        Returns:
            Updated TokenInfo with new access token.

        Raises:
            TwitchTokenRefreshError: If refresh fails.
        """
        if self._token_info is None:
            raise TwitchAuthError("No token to refresh")

        client = await self._get_http_client()
        response = await client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._token_info.refresh_token,
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
            },
        )

        if response.status_code != 200:
            raise TwitchTokenRefreshError(f"Failed to refresh token: {response.text}")

        data = response.json()
        self._token_info = TokenInfo(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", self._token_info.refresh_token),
            expires_at=datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600)),
            scopes=data.get("scope", []),
        )

        if self.on_token_refresh:
            self.on_token_refresh(self._token_info)

        return self._token_info

    async def get_token_info(self) -> TokenInfo:
        """Get current token info, initializing if needed."""
        await self.get_token()  # Ensures token is initialized and valid
        return self._token_info

    async def __aenter__(self) -> "TwitchAuth":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
