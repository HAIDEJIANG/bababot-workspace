# Queue API

## Endpoints
`GET`, Endpoint=`/v1/queue/preview`, Description=Preview queue for profile
`GET`, Endpoint=`/v1/queue/next-slot`, Description=Get next available slot
`GET`, Endpoint=`/v1/queue/slots`, Description=Get queue slot configuration
`POST`, Endpoint=`/v1/queue/slots`, Description=Create a new queue
`PUT`, Endpoint=`/v1/queue/slots`, Description=Update queue slots
`DELETE`, Endpoint=`/v1/queue/slots`, Description=Delete a queue schedule

## Add Post to Queue
```bash
curl -X POST https://getlate.dev/api/v1/posts \
 -H "Authorization: Bearer YOUR_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
 "content": "Queued post",
 "platforms": [{ "platform": "twitter", "accountId": "acc_123" }],
 "queuedFromProfile": "PROFILE_ID"
 }'
```

## Preview Queue
curl "https://getlate.dev/api/v1/queue/preview?profileId=PROFILE_ID" \
 -H "Authorization: Bearer YOUR_API_KEY"

Returns upcoming scheduled posts in queue order.

## Get Next Slot
curl "https://getlate.dev/api/v1/queue/next-slot?profileId=PROFILE_ID" \

Returns the next available time slot for posting.

## Configure Queue Slots
curl -X PUT https://getlate.dev/api/v1/queue/slots \
 "profileId": "PROFILE_ID",
 "queueId": "QUEUE_ID",
 "slots": [
 { "dayOfWeek": 1, "time": "09:00" },
 { "dayOfWeek": 1, "time": "12:00" },
 { "dayOfWeek": 1, "time": "18:00" }
 ],
 "timezone": "America/New_York"

Queue slots define when posts are automatically published.
- `dayOfWeek`: 0-6 (0=Sunday, 6=Saturday)
- `time`: 24-hour format "HH:mm"