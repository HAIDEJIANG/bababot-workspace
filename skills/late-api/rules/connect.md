# Connect (OAuth) API

## Endpoints
`GET`, Endpoint=`/v1/connect/{platform}`, Description=Start OAuth flow
`POST`, Endpoint=`/v1/connect/bluesky/credentials`, Description=Connect Bluesky (app password)
`GET`, Endpoint=`/v1/connect/telegram`, Description=Generate Telegram access code
`POST`, Endpoint=`/v1/connect/telegram`, Description=Direct connect via chat ID
`PATCH`, Endpoint=`/v1/connect/telegram`, Description=Poll connection status

## Platform Selection Endpoints
Some platforms require selecting a page/location after OAuth:

| `GET` | `/v1/connect/facebook/select-page` | List Facebook pages |
| `POST` | `/v1/connect/facebook/select-page` | Select Facebook page |
| `GET` | `/v1/connect/linkedin/organizations` | List available LinkedIn orgs |
| `POST` | `/v1/connect/linkedin/select-organization` | Select LinkedIn org |
| `GET` | `/v1/connect/googlebusiness/locations` | List GMB locations |
| `POST` | `/v1/connect/googlebusiness/select-location` | Select GMB location |
| `GET` | `/v1/connect/pinterest/select-board` | List Pinterest boards |
| `POST` | `/v1/connect/pinterest/select-board` | Select Pinterest board |
| `GET` | `/v1/connect/snapchat/select-profile` | List Snapchat profiles |
| `POST` | `/v1/connect/snapchat/select-profile` | Select Snapchat profile |

## OAuth Flow

### Standard OAuth (most platforms)
```bash

# Get OAuth URL
curl "https://getlate.dev/api/v1/connect/twitter?profileId=PROFILE_ID&callbackUrl=https://yourapp.com/callback" \
 -H "Authorization: Bearer YOUR_API_KEY"
```

Returns `{ "url": "https://twitter.com/oauth/..." }` - redirect user there.

### Bluesky (App Password)
curl -X POST https://getlate.dev/api/v1/connect/bluesky/credentials \
 -H "Authorization: Bearer YOUR_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
 "profileId": "PROFILE_ID",
 "identifier": "user.bsky.social",
 "appPassword": "xxxx-xxxx-xxxx-xxxx"
 }'

### Telegram
**Option 1: Access Code Flow (recommended)**

# 1. Generate access code
curl "https://getlate.dev/api/v1/connect/telegram?profileId=PROFILE_ID" \

# 3. Poll for connection status
curl -X PATCH "https://getlate.dev/api/v1/connect/telegram?code=LATE-ABC123" \

# Returns: { "status": "pending" } or { "status": "connected", "account": {...} }
**Option 2: Direct Chat ID (power users)**

curl -X POST https://getlate.dev/api/v1/connect/telegram \
 "chatId": "-1001234567890"

The Late bot must already be added as admin in your channel/group.

## Supported Platforms
Twitter/X, Auth Method=OAuth 2.0 PKCE, Notes=Requires code verifier
Instagram, Auth Method=OAuth 2.0, Notes=2-step token exchange
Facebook, Auth Method=OAuth 2.0, Notes=Requires page selection
LinkedIn, Auth Method=OAuth 2.0, Notes=Optional org selection
TikTok, Auth Method=OAuth 2.0, Notes=UX compliance required
YouTube, Auth Method=Google OAuth, Notes=access_type=offline
Pinterest, Auth Method=OAuth 2.0, Notes=Requires board selection
Reddit, Auth Method=OAuth 2.0, Notes=Strict user-agent
Bluesky, Auth Method=App password, Notes=No OAuth, uses AT Protocol
Threads, Auth Method=OAuth 2.0, Notes=Similar to Instagram
Google Business, Auth Method=Google OAuth, Notes=Requires location selection
Telegram, Auth Method=Chat ID, Notes=Uses Late's bot
Snapchat, Auth Method=OAuth 2.0, Notes=Allowlist-only