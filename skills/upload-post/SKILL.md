---
name: upload-post
description: "Upload content to social media platforms via Upload-Post API. Use when posting videos, photos, text, or documents to TikTok, Instagram, YouTube, LinkedIn, Facebook, X (Twitter), Threads, Pinterest, Reddit, or Bluesky. Supports scheduling, analytics, FFmpeg processing, and upload history."

# Upload-Post API
Post content to multiple social media platforms with a single API call.

## Documentation
- Full API docs: https://docs.upload-post.com
- LLM-friendly: https://docs.upload-post.com/llm.txt

## Setup
1. Create account at [upload-post.com](https://upload-post.com)
2. Connect your social media accounts
3. Create a **Profile** (e.g., "mybrand") - this links your connected accounts
4. Generate an **API Key** from dashboard
5. Use the profile name as `user` parameter in API calls

## Authentication
```
Authorization: Apikey YOUR_API_KEY

Base URL: `https://api.upload-post.com/api`

The `user` parameter in all endpoints refers to your **profile name** (not username), which determines which connected social accounts receive the content.

## Endpoints Reference
`/upload_videos`, Method=POST, Description=Upload videos
`/upload_photos`, Method=POST, Description=Upload photos/carousels
`/upload_text`, Method=POST, Description=Text-only posts
`/upload_document`, Method=POST, Description=Upload documents (LinkedIn only)
`/uploadposts/status?request_id=X`, Method=GET, Description=Check async upload status
`/uploadposts/history`, Method=GET, Description=Upload history
`/uploadposts/schedule`, Method=GET, Description=List scheduled posts
`/uploadposts/schedule/<job_id>`, Method=DELETE, Description=Cancel scheduled post
`/uploadposts/schedule/<job_id>`, Method=PATCH, Description=Edit scheduled post
`/uploadposts/me`, Method=GET, Description=Validate API key
`/analytics/<profile>`, Method=GET, Description=Get analytics
`/uploadposts/facebook/pages`, Method=GET, Description=List Facebook pages
`/uploadposts/linkedin/pages`, Method=GET, Description=List LinkedIn pages
`/uploadposts/pinterest/boards`, Method=GET, Description=List Pinterest boards
`/uploadposts/reddit/detailed-posts`, Method=GET, Description=Get Reddit posts with media
`/ffmpeg`, Method=POST, Description=Process media with FFmpeg

## Upload Videos
```bash
curl -X POST "https://api.upload-post.com/api/upload_videos" \
 -H "Authorization: Apikey YOUR_KEY" \
 -F "user=profile_name" \
 -F "platform[]=instagram" \
 -F "platform[]=tiktok" \
 -F "video=@video.mp4" \
 -F "title=My caption"

Key parameters:
- `user`: Profile username (required)
- `platform[]`: Target platforms (required)
- `video`: Video file or URL (required)
- `title`: Caption/title (required)
- `description`: Extended description
- `scheduled_date`: ISO-8601 date for scheduling
- `timezone`: IANA timezone (e.g., "Europe/Madrid")
- `async_upload`: Set `true` for background processing
- `first_comment`: Auto-post first comment

## Upload Photos
curl -X POST "https://api.upload-post.com/api/upload_photos" \
 -F "photos[]=@photo1.jpg" \
 -F "photos[]=@photo2.jpg" \

Instagram & Threads support mixed carousels (photos + videos in same post).

## Upload Text
curl -X POST "https://api.upload-post.com/api/upload_text" \
 -H "Content-Type: application/json" \
 -d '{
 "user": "profile_name",
 "platform": ["x", "threads", "bluesky"],
 "title": "My text post"
 }'

Supported: X, LinkedIn, Facebook, Threads, Reddit, Bluesky.

## Upload Document (LinkedIn only)
Upload PDFs, PPTs, DOCs as native LinkedIn document posts (carousel viewer).

curl -X POST "https://api.upload-post.com/api/upload_document" \
 -F 'platform[]=linkedin' \
 -F "document=@presentation.pdf" \
 -F "title=Document Title" \
 -F "description=Post text above document"

Parameters:
- `document`: PDF, PPT, PPTX, DOC, DOCX (max 100MB, 300 pages)
- `title`: Document title (required)
- `description`: Post commentary
- `visibility`: PUBLIC, CONNECTIONS, LOGGED_IN, CONTAINER
- `target_linkedin_page_id`: Post to company page

## Supported Platforms
| TikTok | | | - | - |
| Instagram | | | - | - |
| YouTube | | - | - | - |
| LinkedIn | | | | |
| Facebook | | | | - |
| X (Twitter) | | | | - |
| Threads | | | | - |
| Pinterest | | | - | - |
| Reddit | - | | | - |
| Bluesky | | | | - |

## Upload History
curl "https://api.upload-post.com/api/uploadposts/history?page=1&limit=20" \
 -H "Authorization: Apikey YOUR_KEY"

- `page`: Page number (default: 1)
- `limit`: 10, 20, 50, or 100 (default: 10)

Returns: upload timestamp, platform, success status, post URLs, errors.

## Scheduling
Add `scheduled_date` parameter (ISO-8601):

```json
{
 "scheduled_date": "2026-02-01T10:00:00Z",
 "timezone": "Europe/Madrid"
}

Response includes `job_id`. Manage with:
- `GET /uploadposts/schedule` - List all scheduled
- `DELETE /uploadposts/schedule/<job_id>` - Cancel
- `PATCH /uploadposts/schedule/<job_id>` - Edit (date, title, caption)

## Check Upload Status
For async uploads or scheduled posts:

curl "https://api.upload-post.com/api/uploadposts/status?request_id=XXX" \

Or use `job_id` for scheduled posts.

## Analytics
curl "https://api.upload-post.com/api/analytics/profile_name?platforms=instagram,tiktok" \

Supported: Instagram, TikTok, LinkedIn, Facebook, X, YouTube, Threads, Pinterest, Reddit, Bluesky.

Returns: followers, impressions, reach, profile views, time-series data.

# Facebook Pages
curl "https://api.upload-post.com/api/uploadposts/facebook/pages" \

# LinkedIn Pages
curl "https://api.upload-post.com/api/uploadposts/linkedin/pages" \

# Pinterest Boards
curl "https://api.upload-post.com/api/uploadposts/pinterest/boards" \

## Reddit Detailed Posts
Get posts with full media info (images, galleries, videos):

curl "https://api.upload-post.com/api/uploadposts/reddit/detailed-posts?profile_username=myprofile" \

Returns up to 2000 posts with media URLs, dimensions, thumbnails.

## FFmpeg Editor
Process media with custom FFmpeg commands:

curl -X POST "https://api.upload-post.com/api/ffmpeg" \
 -F "file=@input.mp4" \
 -F "full_command=ffmpeg -y -i {input} -c:v libx264 -crf 23 {output}" \
 -F "output_extension=mp4"

- Use `{input}` and `{output}` placeholders
- Poll job status until `FINISHED`
- Download result from `/ffmpeg/job/<job_id>/download`
- Supports multiple inputs: `{input0}`, `{input1}`, etc.

Quotas: Free 30min/mo, Basic 300min, Pro 1000min, Advanced 3000min, Business 10000min.

## Platform-Specific Parameters
See [references/platforms.md](references/platforms.md) for detailed platform parameters.

## Media Requirements
See [references/requirements.md](references/requirements.md) for format specs per platform.

## Error Codes
- 400: Bad request / missing params
- 401: Invalid API key
- 404: Resource not found
- 429: Rate limit / quota exceeded
- 500: Server error

## Notes
- Videos auto-switch to async if >59s processing time
- X long text creates threads unless `x_long_text_as_post=true`
- Facebook requires Page ID (personal profiles not supported by Meta)
- Instagram/Threads support mixed carousels (photos + videos)