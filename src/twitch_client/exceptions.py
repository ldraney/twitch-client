"""Twitch client exceptions."""


class TwitchClientError(Exception):
    """Base exception for twitch-client."""

    pass


class TwitchAuthError(TwitchClientError):
    """Authentication-related errors."""

    pass


class TwitchTokenExpiredError(TwitchAuthError):
    """Token has expired and refresh failed."""

    pass


class TwitchTokenRefreshError(TwitchAuthError):
    """Failed to refresh the access token."""

    pass


class TwitchAPIError(TwitchClientError):
    """API request failed."""

    def __init__(self, status_code: int, message: str, error: str | None = None):
        self.status_code = status_code
        self.message = message
        self.error = error
        super().__init__(f"[{status_code}] {error}: {message}" if error else f"[{status_code}] {message}")


class TwitchRateLimitError(TwitchAPIError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: int | None = None):
        self.retry_after = retry_after
        super().__init__(429, message, "Rate Limited")
