---
name: fathom
description: Connect to Fathom AI to fetch call recordings, transcripts, and summaries. Use when user asks about their meetings, call history, or wants to search past conversations.
read_when:
 - User asks about their Fathom calls or meetings
 - User wants to search call transcripts
 - User needs a call summary or action items
 - User wants to set up Fathom integration
metadata:
 clawdbot:
 emoji: ""
 requires:
 bins: ["curl", "jq"]

# Fathom Skill
Connect to [Fathom AI](https://fathom.video) to fetch call recordings, transcripts, and summaries.

## Setup

### 1. Get Your API Key
1. Go to [developers.fathom.ai](https://developers.fathom.ai)
2. Create an API key
3. Copy the key (format: `v1XDx...`)

### 2. Configure
```bash

# Option A: Store in file (recommended)
echo "YOUR_API_KEY" > ~/.fathom_api_key
chmod 600 ~/.fathom_api_key

# Option B: Environment variable
export FATHOM_API_KEY="YOUR_API_KEY"
```

### 3. Test Connection
./scripts/setup.sh

## Commands

### List Recent Calls
./scripts/list-calls.sh # Last 10 calls
./scripts/list-calls.sh --limit 20 # Last 20 calls
./scripts/list-calls.sh --after 2026-01-01 # Calls after date
./scripts/list-calls.sh --json # Raw JSON output

### Get Transcript
./scripts/get-transcript.sh 123456789 # By recording ID
./scripts/get-transcript.sh 123456789 --json
./scripts/get-transcript.sh 123456789 --text-only

### Get Summary
./scripts/get-summary.sh 123456789 # By recording ID
./scripts/get-summary.sh 123456789 --json

### Search Calls
./scripts/search-calls.sh "product launch" # Search transcripts
./scripts/search-calls.sh --speaker "Lucas"
./scripts/search-calls.sh --after 2026-01-01 --before 2026-01-15

## API Reference
`/meetings`, Method=GET, Description=List meetings with filters
`/recordings/{id}/transcript`, Method=GET, Description=Full transcript with speakers
`/recordings/{id}/summary`, Method=GET, Description=AI summary + action items
`/webhooks`, Method=POST, Description=Register webhook for auto-sync

**Base URL:** `https://api.fathom.ai/external/v1`
**Auth:** `X-API-Key` header

## Filters for list-calls
`--limit N`, Description=Number of results, Example=`--limit 20`
`--after DATE`, Description=Calls after date, Example=`--after 2026-01-01`
`--before DATE`, Description=Calls before date, Example=`--before 2026-01-15`
`--cursor TOKEN`, Description=Pagination cursor, Example=`--cursor eyJo...`

## Output Formats
- `--json`: Raw JSON from API
- `--table`: Formatted table (default for lists)
- `--text-only`: Plain text (transcripts only)

# Get latest call ID
CALL_ID=$(./scripts/list-calls.sh --limit 1 --json | jq -r '.[0].recording_id')

# Get summary
./scripts/get-summary.sh $CALL_ID

### Export all calls from last week
./scripts/list-calls.sh --after $(date -d '7 days ago' +%Y-%m-%d) --json > last_week_calls.json

### Find calls mentioning a topic
./scripts/search-calls.sh "quarterly review"

## Troubleshooting
- "No API key found": Run setup or set `FATHOM_API_KEY`
- "401 Unauthorized": Check API key is valid
- "429 Rate Limited": Wait and retry
- "Recording not found": Verify recording ID exists

## Webhook Setup (Advanced)
For automatic transcript ingestion, see the webhook setup guide:
./scripts/setup-webhook.sh --url https://your-endpoint.com/webhook

Requires a publicly accessible HTTPS endpoint.