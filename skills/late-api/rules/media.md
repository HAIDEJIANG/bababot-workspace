# Media Upload

## Endpoints
`POST`, Endpoint=`/v1/media/presign`, Description=Get presigned upload URL

## Get Presigned URL
```bash
curl -X POST https://getlate.dev/api/v1/media/presign \
 -H "Authorization: Bearer YOUR_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{"filename": "image.jpg", "contentType": "image/jpeg"}'
```

## Upload Flow
```typescript
// 1. Get presigned URL
const { uploadUrl, fileUrl } = await getPresignedUrl('image.jpg', 'image/jpeg');

// 2. Upload to presigned URL
await fetch(uploadUrl, {
 method: 'PUT',
 body: fileBuffer,
 headers: { 'Content-Type': 'image/jpeg' }
});

// 3. Use fileUrl in post
await createPost({
 content: 'Check this out!',
 mediaItems: [{ type: 'image', url: fileUrl }],
 platforms: [{ platform: 'twitter', accountId: 'acc_123' }]

## Supported Formats
Images, Formats=JPG, PNG, WebP, GIF, Max Size=5MB
Videos, Formats=MP4, MOV, WebM, Max Size=5GB
Documents, Formats=PDF (LinkedIn only), Max Size=100MB

## Platform Media Limits
Instagram, Max Images=8MB, Max Video=100MB stories, 300MB reels, Special=4:5 to 1.91:1 aspect
TikTok, Max Images=20MB, Max Video=4GB, 10min max, Special=9:16 strict
Twitter, Max Images=5MB, Max Video=512MB, 2min 20s, Special=1-4 images
LinkedIn, Max Images=8MB, Max Video=5GB, Special=20 image carousel
YouTube, Max Images=2MB thumbnail, Max Video=256GB, Special=Resumable upload
Facebook, Max Images=10MB, Max Video=4GB, Special=10 multi-image
Threads, Max Images=8MB, Max Video=1GB, 5min, Special=10 carousel
Pinterest, Max Images=32MB, Max Video=2GB, Special=Requires cover image
Bluesky, Max Images=1MB, Max Video=50MB, 3min, Special=4 images max
Snapchat, Max Images=20MB, Max Video=500MB, Special=AES encryption required
Google Business, Max Images=5MB, Max Video=N/A, Special=Images only
Reddit, Max Images=20MB, Max Video=N/A, Special=Via URL
Telegram, Max Images=10MB, Max Video=50MB, Special=4096 char limit