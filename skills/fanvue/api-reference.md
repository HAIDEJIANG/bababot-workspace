# Fanvue API Reference
Complete endpoint documentation for the Fanvue API.

## Base URL
```
https://api.fanvue.com

## Required Headers
All requests must include:

Authorization: Bearer <access_token>
X-Fanvue-API-Version: 2025-06-26

---

## Users

### Get Current User
Retrieve the authenticated user's profile.

```http
GET /users/me

**Scope**: `read:self`

**Response**:
```json
{
 "uuid": "user-uuid",
 "username": "creator_name",
 "displayName": "Creator Name",
 "email": "creator@example.com",
 "avatarUrl": "https://...",
 "isCreator": true,
 "createdAt": "2024-01-01T00:00:00Z"
}

## Chats

### List Chats
Get all chat conversations.

GET /chats

**Scope**: `read:chat`

**Query Parameters**:
`limit`, Type=number, Description=Max results per page
`cursor`, Type=string, Description=Pagination cursor

 "data": [
 "userUuid": "fan-uuid",
 "username": "fan_username",
 "displayName": "Fan Name",
 "lastMessage": "Hello!",
 "lastMessageAt": "2024-01-15T12:00:00Z",
 "unreadCount": 2
 ],
 "pagination": {
 "nextCursor": "cursor-string"

### Get Unread Counts
GET /chats/unread

### Create Chat
Start a new conversation.

POST /chats

**Scope**: `write:chat`

**Body**:
 "userUuid": "recipient-uuid"

### Update Chat
Mark as read, set nickname, etc.

PATCH /chats/:userUuid

 "markAsRead": true,
 "nickname": "VIP Fan"

### Get Online Statuses
Check if multiple users are online.

POST /chats/online-statuses

 "userUuids": ["uuid1", "uuid2", "uuid3"]

### Get Chat Media
Get media shared in a specific chat.

GET /chats/media

| `userUuid` | string | Chat partner's UUID |

## Chat Messages

### List Messages
Get messages from a specific chat.

GET /chat-messages

| `limit` | number | Max messages |

 "id": "message-id",
 "content": "Message text",
 "senderUuid": "sender-uuid",
 "createdAt": "2024-01-15T12:00:00Z",
 "mediaUrls": []
 ]

### Send Message
POST /chat-messages

 "recipientUuid": "fan-uuid",
 "content": "Thanks for subscribing!",
 "mediaIds": []

### Send Mass Message
Send to multiple fans at once.

POST /chat-messages/mass

 "recipientUuids": ["uuid1", "uuid2"],
 "content": "New content available!",

### Delete Message
DELETE /chat-messages/:id

## Posts

### List Posts
Get all posts by the authenticated creator.

GET /posts

**Scope**: `read:post`

| `limit` | number | Max results |

### Get Post
Get a single post by UUID.

GET /posts/:uuid

### Create Post
POST /posts

**Scope**: `write:post`

 "content": "Check out my new content!",
 "mediaIds": ["media-uuid-1", "media-uuid-2"],
 "isPinned": false,
 "isSubscribersOnly": true,
 "price": null

### Get Post Tips
GET /posts/:uuid/tips

### Get Post Likes
GET /posts/:uuid/likes

### Get Post Comments
GET /posts/:uuid/comments

## Creators

### List Followers
Get all followers (free follows).

GET /creators/list-followers

**Scope**: `read:creator`

### List Subscribers
Get all active paid subscribers.

GET /creators/list-subscribers

 "userUuid": "subscriber-uuid",
 "username": "fan_name",
 "subscribedAt": "2024-01-01T00:00:00Z",
 "renewsAt": "2024-02-01T00:00:00Z",
 "tier": "premium"

## Insights

### Get Earnings
Retrieve earnings and financial data.

GET /insights/get-earnings

| `period` | string | `day`, `week`, `month`, `year` |
| `startDate` | string | ISO date |
| `endDate` | string | ISO date |

### Get Top Spenders
Identify most active fans.

GET /insights/get-top-spenders

### Get Subscriber Stats
GET /insights/get-subscribers

### Get Fan Insights
Detailed engagement metrics.

GET /insights/get-fan-insights

## Media

### List User Media
Get all uploaded media.

GET /media

**Scope**: `read:media`

| `folderId` | string | Filter by vault folder |

### Get Media by UUID
Get a specific media item with optional signed URLs.

GET /media/:uuid

| `variants` | string | Comma-separated: `main`, `thumbnail`, `blurred` |

> **Important**: Without the `variants` parameter, no URLs are returned. Use `?variants=main,thumbnail,blurred` to get signed CloudFront URLs.

**Response** (with variants):
 "uuid": "media-uuid",
 "status": "ready",
 "mediaType": "image",
 "name": "photo.jpg",
 "description": "AI-generated caption",
 "createdAt": "2024-01-15T10:30:00Z",
 "variants": [
 "uuid": "variant-uuid",
 "variantType": "main",
 "width": 1088,
 "height": 1352,
 "url": "https://media.fanvue.com/private/creator-uuid/images/media-uuid?Expires=...&Signature=..."
 },
 "variantType": "blurred",
 "url": "https://media.fanvue.com/private/.../blurred-images/..."

### Create Upload Session
Start a multipart upload.

POST /media/create-upload-session

 "filename": "photo.jpg",
 "contentType": "image/jpeg",
 "fileSize": 1024000

### Complete Upload Session
Finalize the upload.

PATCH /media/complete-upload-session

 "uploadSessionId": "session-id",
 "parts": [
 { "partNumber": 1, "etag": "etag-value" }

## Vault

### List Folders
Get all vault folders.

GET /vault/folders

### Create Folder
POST /vault/folders

 "name": "My New Folder",
 "parentFolderId": null

## Tracking Links

### List Tracking Links
GET /tracking-links

**Scope**: `write:tracking_links`

### Create Tracking Link
POST /tracking-links

 "name": "Instagram Campaign",
 "destination": "profile"

### Delete Tracking Link
DELETE /tracking-links/:uuid

## Pagination
Most list endpoints return paginated results:

 "data": [...],
 "nextCursor": "cursor-string",
 "hasMore": true

To get the next page, pass `?cursor=cursor-string` to the same endpoint.