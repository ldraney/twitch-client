/**
 * Twitch OAuth Authentication
 *
 * Two flows available:
 * 1. Client Credentials - App-only access (simpler, limited data)
 * 2. Authorization Code - User access (full data, requires browser)
 *
 * Usage:
 *   node auth.js client    # Get app access token
 *   node auth.js user      # Start user auth flow (opens browser)
 *   node auth.js validate  # Check if current token is valid
 *   node auth.js refresh   # Refresh user token
 */

import { config } from 'dotenv';
import { resolve } from 'path';
import { homedir } from 'os';

// Load secrets from ~/twitch-secrets/.env
config({ path: resolve(homedir(), 'twitch-secrets', '.env') });

const CLIENT_ID = process.env.TWITCH_CLIENT_ID;
const CLIENT_SECRET = process.env.TWITCH_CLIENT_SECRET;
const REDIRECT_URI = 'http://localhost:3000/callback';

// Scopes needed for affiliate tracking
const SCOPES = [
  'moderator:read:followers',  // Read follower list/count
  'channel:read:subscriptions', // Read sub count (future)
].join(' ');

async function getClientCredentialsToken() {
  console.log('Getting app access token (client credentials flow)...\n');

  const response = await fetch('https://id.twitch.tv/oauth2/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      grant_type: 'client_credentials',
    }),
  });

  const data = await response.json();

  if (data.access_token) {
    console.log('Success! App access token obtained.');
    console.log(`Token: ${data.access_token.substring(0, 10)}...`);
    console.log(`Expires in: ${data.expires_in} seconds`);
    console.log('\nNote: App tokens can only get PUBLIC data (total follower count).');
    console.log('For detailed data, use user auth: node auth.js user');
    return data;
  } else {
    console.error('Failed:', data);
    return null;
  }
}

function startUserAuthFlow() {
  console.log('Starting user authorization flow...\n');

  const authUrl = new URL('https://id.twitch.tv/oauth2/authorize');
  authUrl.searchParams.set('client_id', CLIENT_ID);
  authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('scope', SCOPES);

  console.log('Open this URL in your browser:');
  console.log(authUrl.toString());
  console.log('\nThen run the callback server: node auth-server.js');
  console.log('After authorizing, you\'ll get an access token.');
}

async function validateToken() {
  const token = process.env.TWITCH_ACCESS_TOKEN;
  if (!token) {
    console.log('No TWITCH_ACCESS_TOKEN found in ~/twitch-secrets/.env');
    return null;
  }

  console.log('Validating access token...\n');

  const response = await fetch('https://id.twitch.tv/oauth2/validate', {
    headers: { 'Authorization': `OAuth ${token}` },
  });

  if (response.ok) {
    const data = await response.json();
    console.log('Token is VALID');
    console.log(`  User: ${data.login}`);
    console.log(`  User ID: ${data.user_id}`);
    console.log(`  Scopes: ${data.scopes.join(', ')}`);
    console.log(`  Expires in: ${data.expires_in} seconds`);
    return data;
  } else {
    console.log('Token is INVALID or EXPIRED');
    console.log('Run: node auth.js refresh');
    return null;
  }
}

async function refreshToken() {
  const refreshToken = process.env.TWITCH_REFRESH_TOKEN;
  if (!refreshToken) {
    console.log('No TWITCH_REFRESH_TOKEN found in ~/twitch-secrets/.env');
    console.log('Run: node auth.js user  (to get a new token)');
    return null;
  }

  console.log('Refreshing access token...\n');

  const response = await fetch('https://id.twitch.tv/oauth2/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
    }),
  });

  const data = await response.json();

  if (data.access_token) {
    console.log('Token refreshed successfully!');
    console.log(`New access token: ${data.access_token.substring(0, 10)}...`);
    console.log(`New refresh token: ${data.refresh_token.substring(0, 10)}...`);
    console.log('\nUpdate ~/twitch-secrets/.env with these values:');
    console.log(`TWITCH_ACCESS_TOKEN=${data.access_token}`);
    console.log(`TWITCH_REFRESH_TOKEN=${data.refresh_token}`);
    return data;
  } else {
    console.error('Refresh failed:', data);
    return null;
  }
}

// Main
const command = process.argv[2] || 'help';

switch (command) {
  case 'client':
    await getClientCredentialsToken();
    break;
  case 'user':
    startUserAuthFlow();
    break;
  case 'validate':
    await validateToken();
    break;
  case 'refresh':
    await refreshToken();
    break;
  default:
    console.log('Twitch OAuth Authentication');
    console.log('============================\n');
    console.log('Commands:');
    console.log('  node auth.js client   - Get app access token (limited data)');
    console.log('  node auth.js user     - Start user auth flow (full data)');
    console.log('  node auth.js validate - Check if current token is valid');
    console.log('  node auth.js refresh  - Refresh expired user token');
    console.log('\nFirst, fill in ~/twitch-secrets/.env with your Client ID and Secret');
    console.log('from https://dev.twitch.tv/console/apps');
}
