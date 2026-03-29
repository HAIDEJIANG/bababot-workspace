# Error Handling

## Error Response Format
```json
{
 "error": "Invalid API key",
 "code": "UNAUTHORIZED",
 "details": {}
}
```

## HTTP Status Codes
400, Code=`BAD_REQUEST`, Meaning=Invalid parameters
401, Code=`UNAUTHORIZED`, Meaning=Invalid/missing API key
403, Code=`FORBIDDEN`, Meaning=Insufficient permissions
404, Code=`NOT_FOUND`, Meaning=Resource not found
422, Code=`VALIDATION_ERROR`, Meaning=Validation failed
429, Code=`RATE_LIMITED`, Meaning=Too many requests
500, Code=`INTERNAL_ERROR`, Meaning=Server error

## Rate Limits
- Free: 60, Build: 120, Accelerate: 600, Unlimited: 1,200

### Rate Limit Headers
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1709294400

### Handle Rate Limits
```typescript
async function fetchWithRetry(url: string, options: RequestInit) {
 const response = await fetch(url, options);

 if (response.status === 429) {
 const resetTime = response.headers.get('X-RateLimit-Reset');
 const waitMs = (Number(resetTime) * 1000) - Date.now();
 await sleep(Math.max(waitMs, 1000));
 return fetchWithRetry(url, options);

 return response;

## Publishing Logs
Check post logs for platform-specific errors:

```bash
curl "https://getlate.dev/api/v1/posts/POST_ID/logs" \
 -H "Authorization: Bearer YOUR_API_KEY"

## Logs API
`GET`, Endpoint=`/v1/logs`, Description=List all publishing logs
`GET`, Endpoint=`/v1/logs/{logId}`, Description=Get specific log entry
`GET`, Endpoint=`/v1/posts/{postId}/logs`, Description=Get logs for a post

Logs are retained for 7 days.