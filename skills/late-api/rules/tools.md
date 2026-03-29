# Tools API
Media download and utility tools. Available to paid plans only.

**Rate limits:** Build (50/day), Accelerate (500/day), Unlimited (unlimited)

## Download Endpoints
`GET`, Endpoint=`/v1/tools/instagram/download`, Description=Download Instagram media
`GET`, Endpoint=`/v1/tools/tiktok/download`, Description=Download TikTok video
`GET`, Endpoint=`/v1/tools/twitter/download`, Description=Download Twitter media
`GET`, Endpoint=`/v1/tools/youtube/download`, Description=Download YouTube video
`GET`, Endpoint=`/v1/tools/linkedin/download`, Description=Download LinkedIn media
`GET`, Endpoint=`/v1/tools/facebook/download`, Description=Download Facebook media
`GET`, Endpoint=`/v1/tools/bluesky/download`, Description=Download Bluesky media

## Download Example
```bash
curl "https://getlate.dev/api/v1/tools/instagram/download?url=https://www.instagram.com/p/ABC123/" \
 -H "Authorization: Bearer YOUR_API_KEY"
```

Response:

```json
{
 "success": true,
 "downloadUrl": "https://storage.getlate.dev/downloads/abc123.mp4"
}

## Utility Endpoints
| `POST` | `/v1/tools/instagram/hashtag-checker` | Check hashtag restrictions |
| `GET` | `/v1/tools/youtube/transcript` | Get YouTube video transcript |

## Hashtag Checker
curl -X POST https://getlate.dev/api/v1/tools/instagram/hashtag-checker \
 -H "Authorization: Bearer YOUR_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{"hashtags": ["travel", "photography", "banned123"]}'

 "results": [
 { "hashtag": "travel", "status": "safe" },
 { "hashtag": "photography", "status": "safe" },
 { "hashtag": "banned123", "status": "restricted", "reason": "Community guidelines" }
 ]

Status values: `safe`, `restricted`, `banned`, `unknown`

## YouTube Transcript
curl "https://getlate.dev/api/v1/tools/youtube/transcript?url=https://youtube.com/watch?v=dQw4w9WgXcQ" \

Returns timestamped transcript of the video.