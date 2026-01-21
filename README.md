# twitch-client

[![PyPI](https://img.shields.io/pypi/v/twitch-client)](https://pypi.org/project/twitch-client/)

Twitch OAuth client with token management and authenticated HTTP requests for the Twitch Helix API.

## Installation

```bash
pip install twitch-client
```

## Credentials Setup

### 1. Get Client ID & Secret

1. Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. Create or select your application
3. Copy the **Client ID** and generate a **Client Secret**

### 2. Get Access & Refresh Tokens

Use the [Twitch CLI](https://dev.twitch.tv/docs/cli/) or an OAuth flow to get tokens:

```bash
twitch token -u -s "chat:read chat:edit channel:manage:broadcast"
```

### 3. Create `.env` File

Create `~/.twitch-secrets/.env` (default location):

```bash
mkdir -p ~/.twitch-secrets
cat > ~/.twitch-secrets/.env << 'EOF'
TWITCH_CLIENT_ID=your_client_id
TWITCH_CLIENT_SECRET=your_client_secret
TWITCH_ACCESS_TOKEN=your_access_token
TWITCH_REFRESH_TOKEN=your_refresh_token
EOF
```

Or set the `TWITCH_ENV_FILE` environment variable to use a custom path.

### Basic Usage

```python
import asyncio
from twitch_client import TwitchHTTPClient

async def main():
    async with TwitchHTTPClient() as client:
        # Get user info
        response = await client.get("/users", params={"login": "twitch"})
        print(response)

asyncio.run(main())
```

### Manual Token Management

```python
from twitch_client import TwitchAuth, TwitchCredentials

async def main():
    # Load credentials
    credentials = TwitchCredentials()

    # Create auth manager
    async with TwitchAuth(credentials) as auth:
        # Get valid token (refreshes automatically if needed)
        token = await auth.get_token()

        # Get token info including scopes
        info = await auth.get_token_info()
        print(f"Scopes: {info.scopes}")

asyncio.run(main())
```

### Custom Credentials Location

```python
import os
os.environ["TWITCH_ENV_FILE"] = "~/my-secrets/.env"

from twitch_client import TwitchHTTPClient
# Will load from custom .env location
```

## Features

- Automatic token refresh before expiration
- Pydantic-based configuration validation
- Async HTTP client with httpx
- Rate limit handling
- Comprehensive error types

## API

### TwitchHTTPClient

The main HTTP client for making authenticated requests:

- `get(endpoint, params)` - GET request
- `post(endpoint, data, params)` - POST request
- `patch(endpoint, data, params)` - PATCH request
- `put(endpoint, data, params)` - PUT request
- `delete(endpoint, params)` - DELETE request

### TwitchAuth

Token management:

- `get_token()` - Get valid access token
- `refresh_token()` - Force token refresh
- `get_token_info()` - Get token metadata and scopes

## Exceptions

- `TwitchClientError` - Base exception
- `TwitchAuthError` - Authentication errors
- `TwitchTokenRefreshError` - Token refresh failed
- `TwitchAPIError` - API request failed
- `TwitchRateLimitError` - Rate limit exceeded
