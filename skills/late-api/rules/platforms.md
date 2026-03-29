# Platform-Specific Features

## Supported Platforms
Twitter/X, OAuth=Yes, Features=Posts, threads, images, videos
Instagram, OAuth=Yes, Features=Feed, Stories, Reels, Carousels
Facebook, OAuth=Yes, Features=Pages, Reels, Stories
LinkedIn, OAuth=Yes, Features=Posts, images, videos, documents
TikTok, OAuth=Yes, Features=Videos with privacy controls
YouTube, OAuth=Yes, Features=Videos, Shorts
Pinterest, OAuth=Yes, Features=Pins with images/videos
Reddit, OAuth=Yes, Features=Posts with subreddit targeting
Bluesky, OAuth=App password, Features=Posts, images, videos
Threads, OAuth=Yes, Features=Posts, images, videos
Google Business, OAuth=Yes, Features=Updates, photos, offers
Telegram, OAuth=Bot token, Features=Messages, images, videos
Snapchat, OAuth=Yes, Features=Stories, Spotlight

## Platform-Specific Data
Platform-specific data goes inside each platform entry in the `platforms` array:

```json
{
 "platforms": [
 "platform": "instagram",
 "accountId": "acc_123",
 "platformSpecificData": { ... }
 }
 ]
```

### Twitter/X
"platformSpecificData": {
 "threadItems": [
 { "content": "Second tweet" },
 { "content": "Third tweet", "mediaItems": [{ "type": "image", "url": "..." }] }

### Instagram
"contentType": "story",
 "firstComment": "First comment!",
 "collaborators": ["username"],
 "shareToFeed": true,
 "userTags": [{ "username": "user", "x": 0.5, "y": 0.5 }],
 "trialParams": { "graduationStrategy": "SS_PERFORMANCE" },
 "audioName": "My Custom Audio",
 "thumbOffset": 5000

- `contentType: "story"` publishes as a Story. Default posts become Reels or feed based on media.
- `trialParams` for Trial Reels (non-followers first): `MANUAL` or `SS_PERFORMANCE` (auto-graduate)
- `audioName` sets custom label for original audio in Reels
- `thumbOffset` selects thumbnail frame (milliseconds from start)

### TikTok
"privacyLevel": "PUBLIC_TO_EVERYONE",
 "allowComment": true,
 "allowDuet": true,
 "allowStitch": true,
 "contentPreviewConfirmed": true,
 "expressConsentGiven": true,
 "draft": false,
 "commercialContentType": "none",
 "videoMadeWithAi": false,
 "videoCoverTimestampMs": 1000,
 "photoCoverIndex": 0,
 "autoAddMusic": false,
 "description": "Extended description for photo posts (max 4000 chars)"

**Required fields:**
- `contentPreviewConfirmed` and `expressConsentGiven` must be `true`
- `allowDuet`, `allowStitch` required for videos; `allowComment` for all

**Optional fields:**
- `draft: true` sends to Creator Inbox instead of publishing
- `commercialContentType`: `none`, `brand_organic`, `brand_content`
- `brandPartnerPromote`: Whether the post promotes a brand partner
- `isBrandOrganicPost`: Whether the post is a brand organic post
- `mediaType`: `video` or `photo` (auto-detected from media)
- `description` for photo posts when content exceeds 90 chars

### YouTube
"title": "Video Title",
 "visibility": "public",
 "firstComment": "Check out my other videos!",
 "containsSyntheticMedia": false

- `visibility`: `public`, `private`, `unlisted`
- `firstComment`: Optional comment posted after upload (max 10,000 chars)
- `containsSyntheticMedia`: Set `true` for AI-generated content disclosure
- Videos ≤3 min auto-detected as Shorts; >3 min as regular videos
- Use top-level `tags` array for video tags (≤500 chars total)

### Pinterest
"title": "Pin Title",
 "boardId": "board_123",
 "link": "https://example.com",
 "coverImageUrl": "https://example.com/cover.jpg",
 "coverImageKeyFrameTime": 5

- `title`: Pin title (max 100 chars, defaults to first line of content)
- `boardId`: Target board (uses first available if omitted)
- `coverImageUrl`: Optional cover image for video pins
- `coverImageKeyFrameTime`: Key frame time in seconds for video cover

### Google Business
"callToAction": {
 "type": "LEARN_MORE",
 "url": "https://example.com"

Action types: `BOOK`, `ORDER`, `SHOP`, `LEARN_MORE`, `SIGN_UP`, `CALL`

### LinkedIn
"firstComment": "First comment on the post",
 "disableLinkPreview": false

Supports up to 20 images, single PDF documents (max 100MB), and link previews for URLs.

### Facebook
"pageId": "123456789"

Set `contentType: "story"` to publish as a Facebook Page Story (24-hour ephemeral). Supports up to 10 images for feed posts.

### Threads
{ "content": "Second post in thread" },
 { "content": "Third post", "mediaItems": [{ "type": "image", "url": "..." }] }

Creates reply chains (Threads equivalent of Twitter threads). Supports up to 10 images per carousel.

### Telegram
"parseMode": "HTML",
 "disableWebPagePreview": false,
 "disableNotification": false,
 "protectContent": false

Parse modes: `HTML`, `Markdown`, `MarkdownV2`. Supports up to 10 images or videos in albums. Max 4096 chars for text-only, 1024 for media captions.

### Snapchat
"contentType": "story"

Content types:
- `story` - Ephemeral (24 hours), no text caption
- `saved_story` - Permanent on Public Profile, title max 45 chars
- `spotlight` - Video for entertainment feed, description max 160 chars