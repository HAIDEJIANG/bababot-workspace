# Home Assistant REST API Reference

## Authentication
All requests require the `Authorization` header:

```
Authorization: Bearer <long-lived-access-token>

## Base Endpoints
`/api/`, Method=GET, Description=API status and HA version
`/api/config`, Method=GET, Description=Current configuration
`/api/states`, Method=GET, Description=All entity states
`/api/states/<entity_id>`, Method=GET, Description=Single entity state
`/api/states/<entity_id>`, Method=POST, Description=Set entity state
`/api/services`, Method=GET, Description=Available services
`/api/services/<domain>/<service>`, Method=POST, Description=Call a service
`/api/events`, Method=GET, Description=Available events
`/api/events/<event_type>`, Method=POST, Description=Fire an event
`/api/history/period/<timestamp>`, Method=GET, Description=State history
`/api/logbook/<timestamp>`, Method=GET, Description=Logbook entries

## Common Services

### Lights
```bash

# Turn on with options
POST /api/services/light/turn_on
{
 "entity_id": "light.living_room",
 "brightness": 255, # 0-255
 "color_temp": 370, # Mireds (153-500 typically)
 "rgb_color": [255, 0, 0], # RGB array
 "transition": 2 # Seconds
}

# Turn off
POST /api/services/light/turn_off
{"entity_id": "light.living_room"}

# Set temperature
POST /api/services/climate/set_temperature
 "entity_id": "climate.thermostat",
 "temperature": 22,
 "hvac_mode": "heat" # heat, cool, auto, off

# Set preset
POST /api/services/climate/set_preset_mode
 "preset_mode": "away"

# Play/pause
POST /api/services/media_player/media_play_pause
{"entity_id": "media_player.tv"}

# Set volume (0.0-1.0)
POST /api/services/media_player/volume_set
{"entity_id": "media_player.tv", "volume_level": 0.5}

# Play media
POST /api/services/media_player/play_media
 "entity_id": "media_player.tv",
 "media_content_type": "music",
 "media_content_id": "spotify:playlist:xyz"

### Cover (Blinds/Garage)
POST /api/services/cover/open_cover
{"entity_id": "cover.garage"}

POST /api/services/cover/close_cover

POST /api/services/cover/set_cover_position
{"entity_id": "cover.blinds", "position": 50} # 0=closed, 100=open

### Notifications
POST /api/services/notify/mobile_app_phone
 "message": "Motion detected!",
 "title": "Security Alert",
 "data": {
 "image": "/local/camera_snapshot.jpg"

## Entity State Object
```json
 "state": "on",
 "attributes": {
 "brightness": 255,
 "color_temp": 370,
 "friendly_name": "Living Room Light",
 "supported_features": 63
 },
 "last_changed": "2024-01-15T10:30:00+00:00",
 "last_updated": "2024-01-15T10:30:00+00:00"

## Webhooks (Inbound to HA)
Trigger automations via webhook:

POST /api/webhook/<webhook_id>
{"custom": "data"}

Create webhook trigger in automation:

```yaml
automation:
 trigger:
 - platform: webhook
 webhook_id: my_webhook_id
 allowed_methods:
 - POST

## WebSocket API
For real-time updates, use the WebSocket API at `ws://ha-url/api/websocket`.

Connection flow:
1. Connect to WebSocket
2. Receive `auth_required`
3. Send `{"type": "auth", "access_token": "TOKEN"}`
4. Receive `auth_ok`
5. Subscribe to events: `{"id": 1, "type": "subscribe_events", "event_type": "state_changed"}`

## Error Responses
- 400: Bad request (invalid JSON or missing fields)
- 401: Unauthorized (invalid/missing token)
- 404: Entity or service not found
- 405: Method not allowed

## Rate Limits
Home Assistant doesn't enforce strict rate limits, but avoid:
- Polling faster than every 1 second
- Bulk updates without batching

Use WebSocket for real-time state tracking instead of polling.