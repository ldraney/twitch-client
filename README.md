# Twitch API Test Client

Test project for learning Twitch Helix API authentication and endpoints.

## Setup

1. Register an app at https://dev.twitch.tv/console/apps
   - Name: `obs-twitch-cli`
   - OAuth Redirect URL: `http://localhost:3000/callback`
   - Category: Application Integration

2. Copy Client ID and generate a Client Secret

3. Fill in `~/twitch-secrets/.env`:
   ```
   TWITCH_CLIENT_ID=your_client_id
   TWITCH_CLIENT_SECRET=your_client_secret
   ```

4. Install dependencies:
   ```bash
   npm install
   ```

## Authentication

```bash
# Get app-only token (limited data - only total follower count)
node auth.js client

# Start user auth flow (full data access)
node auth.js user          # Get auth URL
node auth-server.js        # Start callback server, then open URL in browser

# Check if token is valid
node auth.js validate

# Refresh expired token
node auth.js refresh
```

## Testing API

```bash
# After getting a token, test endpoints:
node test-api.js user       # Get your user info
node test-api.js followers  # Get follower count
node test-api.js stream     # Check if you're live
node test-api.js all        # Run all tests
```

## Rate Limits

- ~800 requests/minute
- Response headers: `Ratelimit-Limit`, `Ratelimit-Remaining`, `Ratelimit-Reset`
- HTTP 429 = rate limited

## Secrets Location

Secrets are stored in `~/twitch-secrets/.env` (separate private repo).
