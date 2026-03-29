# Webhooks

## Endpoints
`GET`, Endpoint=`/v1/webhooks/settings`, Description=Get webhook config
`POST`, Endpoint=`/v1/webhooks/settings`, Description=Create webhook
`PUT`, Endpoint=`/v1/webhooks/settings`, Description=Update webhook
`DELETE`, Endpoint=`/v1/webhooks/settings`, Description=Delete webhook
`POST`, Endpoint=`/v1/webhooks/test`, Description=Test webhook
`GET`, Endpoint=`/v1/webhooks/logs`, Description=Get webhook delivery logs

## Configure Webhooks
```bash
curl -X POST https://getlate.dev/api/v1/webhooks/settings \
 -H "Authorization: Bearer YOUR_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
 "name": "My Webhook",
 "isActive": true,
 "url": "https://your-server.com/webhooks/late",
 "secret": "your_webhook_secret",
 "events": ["post.published", "post.failed", "account.disconnected"]
 }'
```

## Events
- `post.scheduled`: Post scheduled successfully
- `post.published`: Post published to platform
- `post.failed`: Post failed on all platforms
- `post.partial`: Post succeeded on some platforms
- `account.connected`: Account connected
- `account.disconnected`: Account disconnected (token expired)
- `message.received`: New DM/message received (Instagram, Facebook, Telegram)

## Verify Signature
```typescript
import crypto from 'crypto';

function verifyWebhook(payload: string, signature: string, secret: string): boolean {
 const expected = crypto
 .createHmac('sha256', secret)
 .update(payload)
 .digest('hex');
 return crypto.timingSafeEqual(
 Buffer.from(signature),
 Buffer.from(expected)
 );
}

// In your handler
const signature = req.headers['x-late-signature'];
const isValid = verifyWebhook(JSON.stringify(req.body), signature, secret);

## Payload Examples

### Post Event
```json
{
 "event": "post.published",
 "timestamp": "2024-03-01T10:00:00Z",
 "post": {
 "id": "post_123",
 "content": "Hello from Late API!",
 "status": "published",
 "scheduledFor": "2024-03-01T10:00:00Z",
 "publishedAt": "2024-03-01T10:00:05Z",
 "platforms": [
 "platform": "twitter",
 "publishedUrl": "https://twitter.com/user/status/1234567890"
 },
 "platform": "instagram",
 "status": "failed",
 "error": "Rate limit exceeded"
 ]

### Account Event
"event": "account.disconnected",
 "account": {
 "accountId": "acc_456",
 "profileId": "prof_123",
 "username": "myhandle",
 "displayName": "My Account",
 "disconnectionType": "unintentional",
 "reason": "Token expired"