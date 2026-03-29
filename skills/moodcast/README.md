# MoodCast
**Transform any text into emotionally expressive audio with ambient soundscapes.**

MoodCast is a [Moltbot](https://molt.bot) skill that uses ElevenLabs' most advanced features to create compelling audio content. It analyzes your text, adds emotional expression using Eleven v3 audio tags, and can layer ambient soundscapes for immersive experiences.

[![Demo Video](https://img.shields.io/badge/Demo-Watch%20Video-red?style=for-the-badge&logo=youtube)](YOUR_VIDEO_LINK_HERE)
[![Moltbot Skill](https://img.shields.io/badge/Moltbot-Skill-blue?style=for-the-badge)](https://molt.bot)
[![ElevenLabs](https://img.shields.io/badge/Powered%20by-ElevenLabs-purple?style=for-the-badge)](https://elevenlabs.io)

---

## Features
- **Emotion Detection**: Automatically analyzes text and inserts v3 audio tags (`[excited]`, `[whispers]`, `[laughs]`, etc.)
- **Ambient Soundscapes**: Generates matching background sounds using Sound Effects API
- **Multiple Moods**: Pre-configured moods: dramatic, calm, excited, scary, news, story
- **Smart Text Processing**: Auto-splits long text, handles multiple speakers

## Demo
**Input:**
```
Breaking news! Scientists have discovered something incredible.
This could change everything we know about the universe...
I can't believe it.

**MoodCast Output:**
[excited] Breaking news! Scientists have discovered something incredible.
[pause] This could change everything we know about the universe...
[gasps] [whispers] I can't believe it.

*The AI voice delivers this with genuine excitement, dramatic pauses, and a whispered ending.*

## Quick Start

### 1. Install the Skill
```bash

# Option 1: Clone to your Moltbot skills directory
git clone https://github.com/ashutosh887/moodcast ~/.clawdbot/skills/moodcast

# Option 2: Install via MoltHub (recommended)
npx molthub@latest install moodcast

# After installing, move to workspace or use git clone method

### 2. Set Your API Key
export ELEVENLABS_API_KEY="your-api-key-here"

Or add to `~/.clawdbot/moltbot.json`:
```json
{
 "skills": {
 "entries": {
 "moodcast": {
 "enabled": true,
 "apiKey": "your-api-key-here",
 "env": {
 "ELEVENLABS_API_KEY": "your-api-key-here"
 }

Note: `apiKey` automatically maps to `ELEVENLABS_API_KEY` when the skill declares `primaryEnv`.

### 3. Use It!
**Via Moltbot (WhatsApp/Telegram/Discord/iMessage):**
Hey Molty, moodcast this: "It was a dark and stormy night..."

Or use the slash command:
/moodcast "It was a dark and stormy night..."

**Via Command Line:**
python3 ~/.clawdbot/skills/moodcast/scripts/moodcast.py --text "Hello world!"

## Usage Examples

### Basic Usage
python3 moodcast.py --text "This is amazing news!"

### With Mood Preset
python3 moodcast.py --text "The door creaked open slowly..." --mood scary

### With Ambient Sound
python3 moodcast.py --text "Welcome to my café" --ambient "coffee shop busy morning"

### Save to File
python3 moodcast.py --text "Your story here" --output narration.mp3

### Show Enhanced Text
python3 moodcast.py --text "Wow this is great!" --show-enhanced

# Custom voice, model, and output format
python3 moodcast.py --text "Hello" --voice VOICE_ID --model eleven_v3 --output-format mp3_44100_128

# Override mood's default voice
python3 moodcast.py --text "Dramatic scene" --mood dramatic --voice CUSTOM_VOICE_ID

# Skip emotion enhancement
python3 moodcast.py --text "Plain text" --no-enhance

## Supported Audio Tags (Eleven v3)
MoodCast automatically detects emotions and inserts these tags:

### Emotions
- `[excited]`: amazing, incredible, wow, !!!
- `[happy]`: happy, delighted, thrilled
- `[nervous]`: scared, afraid, terrified
- `[angry]`: angry, furious, hate
- `[sorrowful]`: sad, sorry, tragic
- `[calm]`: peaceful, gentle, quiet

### Delivery
- `[whispers]`: Soft, secretive tone
- `[shouts]`: Loud, emphatic delivery
- `[slows down]`: Deliberate pacing
- `[rushed]`: Fast, urgent speech

### Reactions
| `[laughs]` | Natural laughter |
| `[sighs]` | Weary exhale |
| `[gasps]` | Surprise intake |
| `[giggles]` | Light laughter |
| `[pause]` | Dramatic beat |

## Mood Presets
`dramatic`, Voice=Roger, Style=Theatrical, expressive, Best For=Stories, scripts
`calm`, Voice=Lily, Style=Soothing, peaceful, Best For=Meditation, ASMR
`excited`, Voice=Liam, Style=Energetic, upbeat, Best For=News, announcements
`scary`, Voice=Roger (deep), Style=Tense, ominous, Best For=Horror, thrillers
`news`, Voice=Lily, Style=Professional, clear, Best For=Briefings, reports
`story`, Voice=Rachel, Style=Warm, engaging, Best For=Audiobooks, tales

## Configuration

### Command Line Arguments
`--text`, Short=`-t`, Description=Text to convert to speech (required)
`--mood`, Short=`-m`, Description=Mood preset: dramatic, calm, excited, scary, news, story
`--voice`, Short=`-v`, Description=Voice ID (overrides mood's default voice)
`--model`, Short=, Description=Model ID (default: `eleven_v3`)
`--output-format`, Short=, Description=Output format (default: `mp3_44100_128`)
`--ambient`, Short=`-a`, Description=Generate ambient sound effect (prompt)
`--ambient-duration`, Short=, Description=Ambient duration in seconds (max 30, default: 10)
`--output`, Short=`-o`, Description=Save audio to file instead of playing
`--no-enhance`, Short=, Description=Skip automatic emotion enhancement
`--show-enhanced`, Short=, Description=Print enhanced text before generating
`--list-voices`, Short=, Description=List available voices

### Environment Variables
`ELEVENLABS_API_KEY`, Required=Yes, Description=Your ElevenLabs API key, Default=-
`MOODCAST_DEFAULT_VOICE`, Required=No, Description=Default voice ID (overridden by `--voice` or `--mood`), Default=`CwhRBWXzGAHq8TQ4Fs17`
`MOODCAST_MODEL`, Required=No, Description=Default model ID (overridden by `--model`), Default=`eleven_v3`
`MOODCAST_OUTPUT_FORMAT`, Required=No, Description=Default output format (overridden by `--output-format`), Default=`mp3_44100_128`
`MOODCAST_AUTO_AMBIENT`, Required=No, Description=Auto-generate ambient sounds when using `--mood`, Default=-

**Priority order:** CLI arguments > Environment variables > Hardcoded defaults

### Moltbot Config (`~/.clawdbot/moltbot.json`)
"apiKey": "xi-xxxxxxxxxxxx",
 "ELEVENLABS_API_KEY": "xi-xxxxxxxxxxxx",
 "MOODCAST_AUTO_AMBIENT": "true"

Note: `apiKey` is a convenience field that maps to `ELEVENLABS_API_KEY` when `primaryEnv` is set in the skill metadata.

## ElevenLabs APIs Used
This skill demonstrates **deep integration** with multiple ElevenLabs APIs:

### 1. Text-to-Speech (Eleven v3)
- Model: `eleven_v3` for audio tag support
- Format: `mp3_44100_128`
- Features: Full audio tag expression system

### 2. Sound Effects API
- Generates ambient soundscapes from text prompts
- Up to 30 seconds per generation
- Seamless looping support

### 3. Voices API
- Lists available voices
- Supports custom voice selection
- Mood-based voice matching

## Project Structure
moodcast/
├── SKILL.md # Moltbot skill definition (AgentSkills format)
├── README.md # Project documentation
├── requirements.txt # Python dependencies
├── .gitignore # Git ignore rules
├── scripts/
│ └── moodcast.py # Main Python script
└── examples/
 ├── news.txt # News article example
 ├── scary.txt # Horror story example
 ├── dramatic.txt # Dramatic narrative example
 ├── calm.txt # Peaceful scene example
 └── story.txt # Adventure story example

## Skill Installation Locations
Moltbot loads skills from three locations (in precedence order):
1. **Workspace skills**: `<workspace>/skills/moodcast` (per-agent, highest precedence)
2. **Managed skills**: `~/.clawdbot/skills/moodcast` (shared across agents)
3. **Bundled skills**: Shipped with Moltbot install (lowest precedence)

Use `npx molthub@latest install moodcast` to install to the managed directory, or clone directly to your workspace for per-agent installation.

## Technical Details

### API Integration
- **ElevenLabs API usage**: Uses Eleven v3 audio tags (deepest TTS feature), Sound Effects API, Voices API
- **Practical use cases**: Content creators, writers, podcasters, anyone who wants expressive audio
- **Demo approach**: Single clear hook: "Text that feels emotion" with live demonstration

## License
MIT License - feel free to use, modify, and share!

## Acknowledgments
- [ElevenLabs](https://elevenlabs.io) for the incredible audio AI APIs
- [Moltbot](https://molt.bot) / [Peter Steinberger](https://twitter.com/steipete) for the amazing AI assistant platform

Built for the #ClawdEleven Hackathon (ElevenLabs × Moltbot)