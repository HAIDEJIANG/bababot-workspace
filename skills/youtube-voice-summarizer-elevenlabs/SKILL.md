---
name: youtube-voice-summarizer
version: 1.0.0
description: Transform YouTube videos into podcast-style voice summaries using ElevenLabs TTS
author: Francisco Cordoba
homepage: https://github.com/Franciscomoney/elevenlabs-moltbot
license: MIT
user-invocable: true
metadata: {"openclaw":{"emoji":"️","autoTrigger":{"patterns":["youtube.com/watch","youtu.be/","youtube.com/shorts"]}}}

# YouTube Voice Summarizer
Transform any YouTube video into a professional voice summary delivered in under 60 seconds.

## What It Does
When a user sends a YouTube URL, this skill:
1. Extracts the video transcript via Supadata
2. Generates a concise AI summary via OpenRouter/Cerebras
3. Converts the summary to natural speech via ElevenLabs
4. Returns an audio file the user can listen to

## Requirements
This skill requires a running backend server. Deploy the summarizer service:

```bash
git clone https://github.com/Franciscomoney/elevenlabs-moltbot.git
cd elevenlabs-moltbot
npm install
cp .env.example .env

# Add your API keys to .env
npm start
```

### Required API Keys
ElevenLabs, Purpose=Text-to-speech, Get Key=https://elevenlabs.io
Supadata, Purpose=YouTube transcripts, Get Key=https://supadata.ai
OpenRouter, Purpose=AI summarization, Get Key=https://openrouter.ai

## How to Use
When user sends a YouTube URL:

### Step 1: Start the voice summary job
curl -s -X POST http://127.0.0.1:3050/api/summarize \
 -H "Content-Type: application/json" \
 -d '{"url":"YOUTUBE_URL","length":"short","voice":"podcast"}'

Returns: `{"jobId": "job_xxx", "status": "processing"}`

### Step 2: Poll for completion (wait 3-5 seconds between checks)
curl -s http://127.0.0.1:3050/api/status/JOB_ID

Keep polling until status is "completed".

### Step 3: Return the audio to user
When complete, the response includes:
- `result.audioUrl` - The MP3 audio URL (send this to the user!)
- `result.teaser` - Short hook text about the content
- `result.summary` - Full text summary
- `result.keyPoints` - Array of key takeaways

Send the user:
1. The teaser text as a message
2. The audio URL so they can listen

## Voice Options
- `podcast`: Deep male narrator (default)
- `news`: British authoritative
- `casual`: Friendly conversational
- `female_warm`: Warm female voice

## Summary Lengths
`short`, Duration=1-2 min, Best For=Quick overview
`medium`, Duration=3-5 min, Best For=Balanced detail
`detailed`, Duration=5-10 min, Best For=Comprehensive

## Example Flow
User: "Summarize this: https://www.youtube.com/watch?v=dQw4w9WgXcQ"

1. Start job:
 -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","length":"short","voice":"podcast"}'

2. Poll status with the returned jobId
3. When complete, send the audioUrl to the user

## Text-Only Summary (No Audio)
For faster, cheaper text-only summaries:

curl -s -X POST http://127.0.0.1:3050/api/quick-summary \
 -d '{"url":"YOUTUBE_URL","length":"short"}'

## Troubleshooting
**"Video may not have captions"**
- The video needs subtitles enabled on YouTube
- Auto-generated captions may take time on new videos

**Audio URL not working**
- Ensure BASE_URL in .env is publicly accessible
- Check firewall allows traffic on port 3050

## Cost Per Summary
- Supadata: ~$0.001, OpenRouter: ~$0.005-0.02, ElevenLabs: ~$0.05-0.15, **Total**: **~$0.06-0.17**