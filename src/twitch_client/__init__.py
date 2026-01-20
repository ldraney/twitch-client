"""Twitch OAuth client with token management and authenticated HTTP requests."""

from .auth import TokenInfo, TwitchAuth, TwitchCredentials
from .exceptions import (
    TwitchAPIError,
    TwitchAuthError,
    TwitchClientError,
    TwitchRateLimitError,
    TwitchTokenExpiredError,
    TwitchTokenRefreshError,
)
from .http import TwitchHTTPClient

__all__ = [
    "TwitchAuth",
    "TwitchCredentials",
    "TwitchHTTPClient",
    "TokenInfo",
    "TwitchClientError",
    "TwitchAuthError",
    "TwitchTokenExpiredError",
    "TwitchTokenRefreshError",
    "TwitchAPIError",
    "TwitchRateLimitError",
]

__version__ = "0.1.0"
