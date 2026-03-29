# AgentMail API Reference

## Inboxes

### Create Inbox
```python
inbox = client.inboxes.create(
 username="my-agent", # Optional: custom username
 client_id="unique-id" # Optional: for idempotency
)
```

**Returns:** `Inbox` object
- `inbox_id`: Email address, `display_name`: Display name, `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### List Inboxes
response = client.inboxes.list(
 limit=10, # Optional: max results
 cursor=None # Optional: pagination cursor

**Returns:** `ListInboxesResponse`
- `inboxes`: List of Inbox objects
- `count`: Total count
- `next_page_token`: Cursor for next page

### Get Inbox
inbox = client.inboxes.get(
 inbox_id='address@agentmail.to'

### Delete Inbox
client.inboxes.delete(

## Messages

### Send Message
message = client.inboxes.messages.send(
 inbox_id='sender@agentmail.to',
 to='recipient@example.com',
 cc=['cc@example.com'], # Optional
 bcc=['bcc@example.com'], # Optional
 subject='Subject',
 text='Plain text body',
 html='<html>...</html>', # Optional
 labels=['tag1', 'tag2'], # Optional
 attachments=[ # Optional
 SendAttachment(
 filename='file.pdf',
 content=b'bytes_or_base64'
 ]

**Returns:** `Message` object
- `message_id`: Unique ID, `thread_id`: Conversation thread, `inbox_id`: Sender inbox
- `subject`, `text`, `html`: Content
- `from_`: Sender address
- `to`, `cc`, `bcc`: Recipients
- `attachments`: List of attachments

### List Messages
messages = client.inboxes.messages.list(
 inbox_id='address@agentmail.to',
 limit=10,
 cursor=None

### Get Message
message = client.inboxes.messages.get(
 message_id='msg_id'

### Reply to Message
reply = client.inboxes.messages.reply(
 message_id='original_msg_id',
 text='Reply text',
 attachments=[] # Optional

### Watch Messages (WebSocket)
for message in client.inboxes.messages.watch(
):
 print(f"New: {message.subject}")

## Attachments

### Download Attachment
content = client.attachments.download(
 attachment_id='att_id'

# Returns: bytes

## Webhooks

### Create Webhook
webhook = client.webhooks.create(
 url='https://example.com/webhook',
 client_id='my-processor',
 events=['message.received', 'message.sent']

**Events:**
- `message.received` - New email received
- `message.sent` - Email sent
- `message.read` - Email marked as read

### List Webhooks
webhooks = client.webhooks.list()

### Delete Webhook
client.webhooks.delete(webhook_id='wh_id')

## Data Types

### Inbox
{
 "inbox_id": "user@agentmail.to",
 "display_name": "Display Name",
 "pod_id": "uuid",
 "client_id": "optional-client-id",
 "created_at": datetime,
 "updated_at": datetime
}

### Message
"message_id": "msg_uuid",
 "thread_id": "thread_uuid",
 "subject": "Subject",
 "text": "Plain text",
 "html": "<html>...</html>",
 "from_": "sender@example.com",
 "to": ["recipient@example.com"],
 "cc": [],
 "bcc": [],
 "date": datetime,
 "attachments": [Attachment]

### Attachment
"attachment_id": "att_uuid",
 "filename": "document.pdf",
 "content_type": "application/pdf",
 "size": 12345

## Error Handling
Common exceptions:
- `LimitExceededError` - Inbox limit reached
- `AuthenticationError` - Invalid API key
- `NotFoundError` - Resource not found
- `RateLimitError` - Too many requests

from agentmail.errors import LimitExceededError

try:
 inbox = client.inboxes.create()
except LimitExceededError:
 print("Inbox limit reached")
except Exception as e:
 print(f"Error: {e}")