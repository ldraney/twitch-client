/**
 * OAuth Callback Server
 *
 * Handles the redirect from Twitch after user authorization.
 * Exchanges the auth code for access + refresh tokens.
 *
 * Usage:
 *   1. Run: node auth.js user     (get the auth URL)
 *   2. Run: node auth-server.js   (start this server)
 *   3. Open the auth URL in browser and authorize
 *   4. Server will exchange code for tokens
 */

import { createServer } from 'http';
import { config } from 'dotenv';
import { resolve } from 'path';
import { homedir } from 'os';

// Load secrets from ~/twitch-secrets/.env
config({ path: resolve(homedir(), 'twitch-secrets', '.env') });

const CLIENT_ID = process.env.TWITCH_CLIENT_ID;
const CLIENT_SECRET = process.env.TWITCH_CLIENT_SECRET;
const REDIRECT_URI = 'http://localhost:3000/callback';
const PORT = 3000;

async function exchangeCodeForToken(code) {
  const response = await fetch('https://id.twitch.tv/oauth2/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      code: code,
      grant_type: 'authorization_code',
      redirect_uri: REDIRECT_URI,
    }),
  });

  return response.json();
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  if (url.pathname === '/callback') {
    const code = url.searchParams.get('code');
    const error = url.searchParams.get('error');

    if (error) {
      res.writeHead(400, { 'Content-Type': 'text/html' });
      res.end(`<h1>Authorization Failed</h1><p>Error: ${error}</p>`);
      console.log('\nAuthorization denied by user');
      return;
    }

    if (code) {
      console.log('\nReceived authorization code, exchanging for token...');

      const tokens = await exchangeCodeForToken(code);

      if (tokens.access_token) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(`
          <h1>Authorization Successful!</h1>
          <p>You can close this window.</p>
          <p>Check your terminal for the tokens.</p>
        `);

        console.log('\n========================================');
        console.log('SUCCESS! Update ~/twitch-secrets/.env:');
        console.log('========================================\n');
        console.log(`TWITCH_ACCESS_TOKEN=${tokens.access_token}`);
        console.log(`TWITCH_REFRESH_TOKEN=${tokens.refresh_token}`);
        console.log('\n========================================');
        console.log(`Token expires in: ${tokens.expires_in} seconds`);
        console.log('Scopes:', tokens.scope?.join(', ') || 'none');
        console.log('========================================\n');

        // Shutdown server after success
        setTimeout(() => {
          console.log('Shutting down server...');
          process.exit(0);
        }, 1000);
      } else {
        res.writeHead(500, { 'Content-Type': 'text/html' });
        res.end(`<h1>Token Exchange Failed</h1><pre>${JSON.stringify(tokens, null, 2)}</pre>`);
        console.error('Token exchange failed:', tokens);
      }
    }
  } else {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Twitch OAuth Callback Server\nWaiting for authorization...');
  }
});

server.listen(PORT, () => {
  console.log(`OAuth callback server running on http://localhost:${PORT}`);
  console.log('Waiting for Twitch authorization callback...');
  console.log('\nMake sure you\'ve opened the auth URL from: node auth.js user');
});
