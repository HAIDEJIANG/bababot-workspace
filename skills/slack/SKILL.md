---
name: slack
description: Use when you need to control Slack from Clawdbot via the slack tool, including reacting to messages or pinning/unpinning items in Slack channels or DMs.

# Slack Actions

## Overview
Use `slack` to react, manage pins, send/edit/delete messages, and fetch member info. The tool uses the bot token configured for Clawdbot.

## Inputs to collect
- `channelId` and `messageId` (Slack message timestamp, e.g. `1712023032.1234`).
- For reactions, an `emoji` (Unicode or `:name:`).
- For message sends, a `to` target (`channel:<id>` or `user:<id>`) and `content`.

Message context lines include `slack message id` and `channel` fields you can reuse directly.

## Actions

### Action groups
reactions, Default=enabled, Notes=React + list reactions
messages, Default=enabled, Notes=Read/send/edit/delete
pins, Default=enabled, Notes=Pin/unpin/list
memberInfo, Default=enabled, Notes=Member info
emojiList, Default=enabled, Notes=Custom emoji list

### React to a message
```json
{
 "action": "react",
 "channelId": "C123",
 "messageId": "1712023032.1234",
 "emoji": ""
}
```

### List reactions
"action": "reactions",
 "messageId": "1712023032.1234"

### Send a message
"action": "sendMessage",
 "to": "channel:C123",
 "content": "Hello from Clawdbot"

### Edit a message
"action": "editMessage",
 "content": "Updated text"

### Delete a message
"action": "deleteMessage",

### Read recent messages
"action": "readMessages",
 "limit": 20

### Pin a message
"action": "pinMessage",

### Unpin a message
"action": "unpinMessage",

### List pinned items
"action": "listPins",
 "channelId": "C123"

### Member info
"action": "memberInfo",
 "userId": "U123"

### Emoji list
"action": "emojiList"

## Ideas to try
- React with to mark completed tasks.
- Pin key decisions or weekly status updates.