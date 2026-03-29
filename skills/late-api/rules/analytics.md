# Analytics API

## Endpoints
`GET`, Endpoint=`/v1/analytics`, Description=Get general analytics
`GET`, Endpoint=`/v1/analytics/youtube/daily-views`, Description=Get YouTube video daily views
`GET`, Endpoint=`/v1/accounts/{accountId}/linkedin-aggregate-analytics`, Description=LinkedIn account analytics
`GET`, Endpoint=`/v1/accounts/{accountId}/linkedin-post-analytics`, Description=LinkedIn post analytics
`GET`, Endpoint=`/v1/accounts/follower-stats`, Description=Follower count history

## YouTube Daily Views
```bash
curl "https://getlate.dev/api/v1/analytics/youtube/daily-views?accountId=ACCOUNT_ID&videoId=VIDEO_ID&startDate=2024-01-01&endDate=2024-01-31" \
 -H "Authorization: Bearer YOUR_API_KEY"
```

Response:

```json
{
 "success": true,
 "videoId": "dQw4w9WgXcQ",
 "dateRange": {
 "startDate": "2024-01-01",
 "endDate": "2024-01-31"
 },
 "totalViews": 15420,
 "dailyViews": [
 "date": "2024-01-01",
 "views": 523,
 "estimatedMinutesWatched": 1045,
 "averageViewDuration": 120,
 "subscribersGained": 12,
 "subscribersLost": 2,
 "likes": 45,
 "comments": 8,
 "shares": 15
 }
 ]

**Note:** Requires `yt-analytics.readonly` scope. If missing, response includes `reauthorizeUrl`.

# Aggregate analytics for account
curl "https://getlate.dev/api/v1/accounts/ACCOUNT_ID/linkedin-aggregate-analytics" \

# Analytics for specific post
curl "https://getlate.dev/api/v1/accounts/ACCOUNT_ID/linkedin-post-analytics?postUrn=URN" \

## Follower Stats
curl "https://getlate.dev/api/v1/accounts/follower-stats?profileId=PROFILE_ID" \

Returns historical follower counts across all connected accounts.