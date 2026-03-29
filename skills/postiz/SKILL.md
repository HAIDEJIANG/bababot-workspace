---
name: postiz
description: Postiz is a tool to schedule social media and chat posts to 28+ channels X, LinkedIn, LinkedIn Page, Reddit, Instagram, Facebook Page, Threads, YouTube, Google My Business, TikTok, Pinterest, Dribbble, Discord, Slack, Kick, Twitch, Mastodon, Bluesky, Lemmy, Farcaster, Telegram, Nostr, VK, Medium, Dev.to, Hashnode, WordPress, ListMonk
homepage: https://docs.postiz.com/public-api/introduction
metadata: {"clawdbot":{"emoji":"","requires":{"bins":[],"env":["POSTIZ_API_KEY"]}}}

# Postiz Skill
Postiz is a tool to schedule social media and chat posts to 28+ channels:

X, LinkedIn, LinkedIn Page, Reddit, Instagram, Facebook Page, Threads, YouTube, Google My Business, TikTok, Pinterest, Dribbble, Discord, Slack, Kick, Twitch, Mastodon, Bluesky, Lemmy, Farcaster, Telegram, Nostr, VK, Medium, Dev.to, Hashnode, WordPress, ListMonk

## Setup
1. Get your API key: https://platform.postiz.com/settings
2. Click on "Settings"
3. Click "Reveal"
4. Set environment variables:
 ```bash
 export POSTIZ_API_KEY="your-api-key"
 ```

## Get all added channels
curl -X GET "https://api.postiz.com/public/v1/integrations" \
 -H "Authorization: $POSTIZ_API_KEY"

## Get the next available slot for a channel
curl -X GET "https://api.postiz.com/public/v1/find-slot/:id" \

## Upload a new file (form-data)
curl -X POST "https://api.postiz.com/public/v1/upload" \
 -H "Authorization: $POSTIZ_API_KEY" \
 -F "file=@/path/to/your/file.png"

## Upload a new file from an existing URL
curl -X POST "https://api.postiz.com/public/v1/upload-from-url" \
 -H "Content-Type: application/json" \
 -d '{
 "url": "https://example.com/image.png"
 }'

## Post list
curl -X GET "https://api.postiz.com/public/v1/posts?startDate=2024-12-14T08:18:54.274Z&endDate=2024-12-14T08:18:54.274Z&customer=optionalCustomerId" \

## Schedule a new post
Settings for different channels can be found in:
https://docs.postiz.com/public-api/introduction
On the bottom left menu

curl -X POST "https://api.postiz.com/public/v1/posts" \
 "type": "schedule",
 "date": "2024-12-14T10:00:00.000Z",
 "shortLink": false,
 "tags": [],
 "posts": [
 {
 "integration": {
 "id": "your-x-integration-id"
 },
 "value": [
 "content": "Hello from the Postiz API! ",
 "image": [{ "id": "img-123", "path": "https://uploads.postiz.com/photo.jpg" }]
 }
 ],
 "settings": {
 "__type": "provider name",
 rest of the settings
 ]

## Delete a post
curl -X DELETE "https://api.postiz.com/public/v1/posts/:id" \