/**
 * Twitch API Test Client
 *
 * Test various Twitch Helix API endpoints to understand
 * rate limits and response formats.
 *
 * Usage:
 *   node test-api.js user           - Get user info
 *   node test-api.js followers      - Get follower count
 *   node test-api.js stream         - Check if live + viewer count
 *   node test-api.js all            - Run all tests
 */

import { config } from 'dotenv';
import { resolve } from 'path';
import { homedir } from 'os';

// Load secrets from ~/twitch-secrets/.env
config({ path: resolve(homedir(), 'twitch-secrets', '.env') });

const CLIENT_ID = process.env.TWITCH_CLIENT_ID;
const ACCESS_TOKEN = process.env.TWITCH_ACCESS_TOKEN;
const USERNAME = process.env.TWITCH_USERNAME || 'devopsphilosopher';

const API_BASE = 'https://api.twitch.tv/helix';

async function apiCall(endpoint) {
  const url = `${API_BASE}${endpoint}`;
  console.log(`GET ${url}\n`);

  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${ACCESS_TOKEN}`,
      'Client-Id': CLIENT_ID,
    },
  });

  // Log rate limit headers
  console.log('Rate Limit Info:');
  console.log(`  Limit: ${response.headers.get('Ratelimit-Limit')}`);
  console.log(`  Remaining: ${response.headers.get('Ratelimit-Remaining')}`);
  console.log(`  Reset: ${response.headers.get('Ratelimit-Reset')}`);
  console.log('');

  const data = await response.json();
  return { status: response.status, data };
}

async function getUser() {
  console.log('=== GET USER INFO ===\n');
  const result = await apiCall(`/users?login=${USERNAME}`);

  if (result.data.data?.length > 0) {
    const user = result.data.data[0];
    console.log('User found:');
    console.log(`  ID: ${user.id}`);
    console.log(`  Login: ${user.login}`);
    console.log(`  Display Name: ${user.display_name}`);
    console.log(`  Type: ${user.type || 'normal'}`);
    console.log(`  Broadcaster Type: ${user.broadcaster_type || 'none'}`);
    console.log(`  Created: ${user.created_at}`);
    return user;
  } else {
    console.log('User not found');
    return null;
  }
}

async function getFollowers(broadcasterId) {
  console.log('\n=== GET FOLLOWERS ===\n');
  const result = await apiCall(`/channels/followers?broadcaster_id=${broadcasterId}`);

  console.log(`Total followers: ${result.data.total}`);

  if (result.data.data?.length > 0) {
    console.log('\nRecent followers:');
    result.data.data.slice(0, 5).forEach(f => {
      console.log(`  - ${f.user_name} (followed: ${f.followed_at})`);
    });
  }

  return result.data.total;
}

async function getStream(userId) {
  console.log('\n=== GET STREAM STATUS ===\n');
  const result = await apiCall(`/streams?user_id=${userId}`);

  if (result.data.data?.length > 0) {
    const stream = result.data.data[0];
    console.log('LIVE!');
    console.log(`  Title: ${stream.title}`);
    console.log(`  Game: ${stream.game_name}`);
    console.log(`  Viewers: ${stream.viewer_count}`);
    console.log(`  Started: ${stream.started_at}`);
    return stream;
  } else {
    console.log('Not currently live');
    return null;
  }
}

// Main
const command = process.argv[2] || 'help';

if (!ACCESS_TOKEN) {
  console.log('No TWITCH_ACCESS_TOKEN found in ~/twitch-secrets/.env');
  console.log('Run: node auth.js  (for auth options)');
  process.exit(1);
}

switch (command) {
  case 'user': {
    await getUser();
    break;
  }
  case 'followers': {
    const user = await getUser();
    if (user) await getFollowers(user.id);
    break;
  }
  case 'stream': {
    const user = await getUser();
    if (user) await getStream(user.id);
    break;
  }
  case 'all': {
    const user = await getUser();
    if (user) {
      await getFollowers(user.id);
      await getStream(user.id);
    }
    console.log('\n=== SUMMARY ===');
    console.log('All endpoints tested. See rate limits above.');
    break;
  }
  default:
    console.log('Twitch API Test Client');
    console.log('======================\n');
    console.log('Commands:');
    console.log('  node test-api.js user       - Get user info');
    console.log('  node test-api.js followers  - Get follower count');
    console.log('  node test-api.js stream     - Check if live');
    console.log('  node test-api.js all        - Run all tests');
    console.log('\nMake sure you have a valid token: node auth.js validate');
}
