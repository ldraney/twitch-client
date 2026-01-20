# CLAUDE.md - twitch-client

## Project Overview

This is the authentication layer for the Twitch Python SDK ecosystem. It handles OAuth token management and provides an authenticated HTTP client for the Twitch Helix API.

## Architecture

```
twitch-client/
├── src/twitch_client/
│   ├── __init__.py      # Public exports
│   ├── auth.py          # TwitchAuth, TwitchCredentials, TokenInfo
│   ├── http.py          # TwitchHTTPClient
│   └── exceptions.py    # All exception types
└── tests/
```

## Key Classes

- **TwitchCredentials**: Pydantic settings model that loads from environment/`.env`
- **TwitchAuth**: Manages tokens, validates, and auto-refreshes
- **TwitchHTTPClient**: Authenticated httpx client for Helix API

## Credentials Location

Default: `~/twitch-secrets/.env`
Override: Set `TWITCH_ENV_FILE` environment variable

## Common Tasks

```bash
# Install dependencies
cd ~/twitch-client && poetry install

# Run tests
poetry run pytest

# Test import
poetry run python -c "from twitch_client import TwitchHTTPClient; print('ok')"
```

## Dependencies

- httpx: Async HTTP
- pydantic: Config validation
- pydantic-settings: Environment loading

## Used By

- `twitch-sdk` - Uses TwitchHTTPClient for all API calls
