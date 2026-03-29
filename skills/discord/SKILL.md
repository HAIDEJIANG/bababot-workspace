---
name: discord
description: Use when you need to control Discord from Clawdbot via the discord tool: send messages, react, post or upload stickers, upload emojis, run polls, manage threads/pins/search, fetch permissions or member/role/channel info, or handle moderation actions in Discord DMs or channels.

# Discord Actions

## Overview
Use `discord` to manage messages, reactions, threads, polls, and moderation. You can disable groups via `discord.actions.*` (defaults to enabled, except roles/moderation). The tool uses the bot token configured for Clawdbot.

## Inputs to collect
- For reactions: `channelId`, `messageId`, and an `emoji`.
- For stickers/polls/sendMessage: a `to` target (`channel:<id>` or `user:<id>`). Optional `content` text.
- Polls also need a `question` plus 2–10 `answers`.
- For media: `mediaUrl` with `file:///path` for local files or `https://...` for remote.
- For emoji uploads: `guildId`, `name`, `mediaUrl`, optional `roleIds` (limit 256KB, PNG/JPG/GIF).
- For sticker uploads: `guildId`, `name`, `description`, `tags`, `mediaUrl` (limit 512KB, PNG/APNG/Lottie JSON).

Message context lines include `discord message id` and `channel` fields you can reuse directly.

**Note:** `sendMessage` uses `to: "channel:<id>"` format, not `channelId`. Other actions like `react`, `readMessages`, `editMessage` use `channelId` directly.

## Actions

### React to a message
```json
{
 "action": "react",
 "channelId": "123",
 "messageId": "456",
 "emoji": ""
}
```

### List reactions + users
"action": "reactions",
 "limit": 100

### Send a sticker
"action": "sticker",
 "to": "channel:123",
 "stickerIds": ["9876543210"],
 "content": "Nice work!"

- Up to 3 sticker IDs per message.
- `to` can be `user:<id>` for DMs.

### Upload a custom emoji
"action": "emojiUpload",
 "guildId": "999",
 "name": "party_blob",
 "mediaUrl": "file:///tmp/party.png",
 "roleIds": ["222"]

- Emoji images must be PNG/JPG/GIF and <= 256KB.
- `roleIds` is optional; omit to make the emoji available to everyone.

### Upload a sticker
"action": "stickerUpload",
 "name": "clawdbot_wave",
 "description": "Clawdbot waving hello",
 "tags": "",
 "mediaUrl": "file:///tmp/wave.png"

- Stickers require `name`, `description`, and `tags`.
- Uploads must be PNG/APNG/Lottie JSON and <= 512KB.

### Create a poll
"action": "poll",
 "question": "Lunch?",
 "answers": ["Pizza", "Sushi", "Salad"],
 "allowMultiselect": false,
 "durationHours": 24,
 "content": "Vote now"

- `durationHours` defaults to 24; max 32 days (768 hours).

### Check bot permissions for a channel
"action": "permissions",
 "channelId": "123"

## Ideas to try
- React with /️ to mark status updates.
- Post a quick poll for release decisions or meeting times.
- Send celebratory stickers after successful deploys.
- Upload new emojis/stickers for release moments.
- Run weekly "priority check" polls in team channels.
- DM stickers as acknowledgements when a user's request is completed.

## Action gating
Use `discord.actions.*` to disable action groups:
- `reactions` (react + reactions list + emojiList)
- `stickers`, `polls`, `permissions`, `messages`, `threads`, `pins`, `search`
- `emojiUploads`, `stickerUploads`
- `memberInfo`, `roleInfo`, `channelInfo`, `voiceStatus`, `events`
- `roles` (role add/remove, default `false`)
- `moderation` (timeout/kick/ban, default `false`)

### Read recent messages
"action": "readMessages",
 "limit": 20

### Send/edit/delete a message
"action": "sendMessage",
 "content": "Hello from Clawdbot"

**With media attachment:**

 "content": "Check out this audio!",
 "mediaUrl": "file:///tmp/audio.mp3"

- `to` uses format `channel:<id>` or `user:<id>` for DMs (not `channelId`!)
- `mediaUrl` supports local files (`file:///path/to/file`) and remote URLs (`https://...`)
- Optional `replyTo` with a message ID to reply to a specific message

 "action": "editMessage",
 "content": "Fixed typo"

 "action": "deleteMessage",
 "messageId": "456"

### Threads
"action": "threadCreate",
 "name": "Bug triage",

 "action": "threadList",
 "guildId": "999"

 "action": "threadReply",
 "channelId": "777",
 "content": "Replying in thread"

### Pins
"action": "pinMessage",

 "action": "listPins",

### Search messages
"action": "searchMessages",
 "content": "release notes",
 "channelIds": ["123", "456"],
 "limit": 10

### Member + role info
"action": "memberInfo",
 "userId": "111"

 "action": "roleInfo",

### List available custom emojis
"action": "emojiList",

### Role changes (disabled by default)
"action": "roleAdd",
 "userId": "111",
 "roleId": "222"

### Channel info
"action": "channelInfo",

 "action": "channelList",

### Voice status
"action": "voiceStatus",

### Scheduled events
"action": "eventList",

### Moderation (disabled by default)
"action": "timeout",
 "durationMinutes": 10

## Discord Writing Style Guide
**Keep it conversational!** Discord is a chat platform, not documentation.

### Do
- Short, punchy messages (1-3 sentences ideal)
- Multiple quick replies > one wall of text
- Use emoji for tone/emphasis
- Lowercase casual style is fine
- Break up info into digestible chunks
- Match the energy of the conversation

### Don't
- No markdown tables (Discord renders them as ugly raw `| text |`)
- No `## Headers` for casual chat (use **bold** or CAPS for emphasis)
- Avoid multi-paragraph essays
- Don't over-explain simple things
- Skip the "I'd be happy to help!" fluff

### Formatting that works
- **bold** for emphasis
- `code` for technical terms
- Lists for multiple items
- > quotes for referencing
- Wrap multiple links in `<>` to suppress embeds

### Example transformations
Bad:
I'd be happy to help with that! Here's a comprehensive overview of the versioning strategies available:

## Semantic Versioning
Semver uses MAJOR.MINOR.PATCH format where...

## Calendar Versioning
CalVer uses date-based versions like...

 Good:
versioning options: semver (1.2.3), calver (2026.01.04), or yolo (`latest` forever). what fits your release cadence?