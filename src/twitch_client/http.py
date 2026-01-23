"""Authenticated HTTP client for Twitch Helix API."""

from typing import Any
from urllib.parse import urlencode

import httpx

from .auth import TwitchAuth, TwitchCredentials
from .exceptions import TwitchAPIError, TwitchRateLimitError


class TwitchHTTPClient:
    """Authenticated HTTP client for Twitch Helix API."""

    BASE_URL = "https://api.twitch.tv/helix"

    def __init__(
        self,
        auth: TwitchAuth | None = None,
        credentials: TwitchCredentials | None = None,
    ):
        """Initialize HTTP client.

        Args:
            auth: TwitchAuth instance. If None, creates one from credentials.
            credentials: Credentials for creating TwitchAuth if auth not provided.
        """
        self.auth = auth or TwitchAuth(credentials)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=30.0,
            )
        return self._client

    async def _get_headers(self) -> dict[str, str]:
        """Get authenticated headers."""
        token = await self.auth.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Client-Id": self.auth.client_id,
            "Content-Type": "application/json",
        }

    async def _get_app_headers(self) -> dict[str, str]:
        """Get headers with app access token."""
        token = await self.auth.get_app_token()
        return {
            "Authorization": f"Bearer {token}",
            "Client-Id": self.auth.client_id,
            "Content-Type": "application/json",
        }

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        if response.status_code == 429:
            retry_after = response.headers.get("Ratelimit-Reset")
            raise TwitchRateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )

        if response.status_code >= 400:
            try:
                data = response.json()
                message = data.get("message", response.text)
                error = data.get("error")
            except Exception:
                message = response.text
                error = None
            raise TwitchAPIError(response.status_code, message, error)

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make authenticated GET request.

        Args:
            endpoint: API endpoint path (e.g., "/users").
            params: Query parameters.

        Returns:
            JSON response as dict.
        """
        client = await self._get_client()
        headers = await self._get_headers()

        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = await client.get(endpoint, headers=headers, params=params)
        self._handle_error_response(response)
        return response.json()

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make authenticated POST request.

        Args:
            endpoint: API endpoint path.
            data: JSON body data.
            params: Query parameters.

        Returns:
            JSON response as dict.
        """
        client = await self._get_client()
        headers = await self._get_headers()

        # Filter out None values
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if data:
            data = {k: v for k, v in data.items() if v is not None}

        response = await client.post(endpoint, headers=headers, json=data, params=params)
        self._handle_error_response(response)

        # Some endpoints return empty responses
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    async def patch(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make authenticated PATCH request.

        Args:
            endpoint: API endpoint path.
            data: JSON body data.
            params: Query parameters.

        Returns:
            JSON response as dict.
        """
        client = await self._get_client()
        headers = await self._get_headers()

        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if data:
            data = {k: v for k, v in data.items() if v is not None}

        response = await client.patch(endpoint, headers=headers, json=data, params=params)
        self._handle_error_response(response)

        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    async def put(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make authenticated PUT request.

        Args:
            endpoint: API endpoint path.
            data: JSON body data.
            params: Query parameters.

        Returns:
            JSON response as dict.
        """
        client = await self._get_client()
        headers = await self._get_headers()

        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if data:
            data = {k: v for k, v in data.items() if v is not None}

        response = await client.put(endpoint, headers=headers, json=data, params=params)
        self._handle_error_response(response)

        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    async def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make authenticated DELETE request.

        Args:
            endpoint: API endpoint path.
            params: Query parameters.

        Returns:
            JSON response as dict (usually empty for DELETE).
        """
        client = await self._get_client()
        headers = await self._get_headers()

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = await client.delete(endpoint, headers=headers, params=params)
        self._handle_error_response(response)

        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    # App-token methods for endpoints requiring app access tokens

    async def get_app(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make GET request with app access token.

        Args:
            endpoint: API endpoint path (e.g., "/eventsub/conduits").
            params: Query parameters.

        Returns:
            JSON response as dict.
        """
        client = await self._get_client()
        headers = await self._get_app_headers()

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = await client.get(endpoint, headers=headers, params=params)
        self._handle_error_response(response)
        return response.json()

    async def post_app(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make POST request with app access token.

        Args:
            endpoint: API endpoint path.
            data: JSON body data.
            params: Query parameters.

        Returns:
            JSON response as dict.
        """
        client = await self._get_client()
        headers = await self._get_app_headers()

        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if data:
            data = {k: v for k, v in data.items() if v is not None}

        response = await client.post(endpoint, headers=headers, json=data, params=params)
        self._handle_error_response(response)

        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    async def patch_app(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make PATCH request with app access token.

        Args:
            endpoint: API endpoint path.
            data: JSON body data.
            params: Query parameters.

        Returns:
            JSON response as dict.
        """
        client = await self._get_client()
        headers = await self._get_app_headers()

        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if data:
            data = {k: v for k, v in data.items() if v is not None}

        response = await client.patch(endpoint, headers=headers, json=data, params=params)
        self._handle_error_response(response)

        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    async def delete_app(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make DELETE request with app access token.

        Args:
            endpoint: API endpoint path.
            params: Query parameters.

        Returns:
            JSON response as dict (usually empty for DELETE).
        """
        client = await self._get_client()
        headers = await self._get_app_headers()

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = await client.delete(endpoint, headers=headers, params=params)
        self._handle_error_response(response)

        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    async def close(self) -> None:
        """Close the HTTP client and auth."""
        if self._client:
            await self._client.aclose()
            self._client = None
        await self.auth.close()

    async def __aenter__(self) -> "TwitchHTTPClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
