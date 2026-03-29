---
name: clawflows
version: 1.0.0
description: Search, install, and run multi-skill automations from clawflows.com. Combine multiple skills into powerful workflows with logic, conditions, and data flow between steps.
metadata:
 clawdbot:
 requires:
 bins: ["clawflows"]
 install:
 - id: node
 kind: node
 package: clawflows
 label: "Install ClawFlows CLI (npm)"

# ClawFlows
Discover and run multi-skill automations that combine capabilities like database, charts, social search, and more.

## Install CLI
```bash
npm i -g clawflows
```

## Commands

### Search for automations
clawflows search "youtube competitor"
clawflows search "morning brief"
clawflows search --capability chart-generation

### Check requirements
Before installing, see what capabilities the automation needs:

clawflows check youtube-competitor-tracker

Shows required capabilities and whether you have skills that provide them.

### Install an automation
clawflows install youtube-competitor-tracker

Downloads to `./automations/youtube-competitor-tracker.yaml`

### List installed automations
clawflows list

### Run an automation
clawflows run youtube-competitor-tracker
clawflows run youtube-competitor-tracker --dry-run

The `--dry-run` flag shows what would happen without executing.

### Enable/disable scheduling
clawflows enable youtube-competitor-tracker # Shows cron setup instructions
clawflows disable youtube-competitor-tracker

### View logs
clawflows logs youtube-competitor-tracker
clawflows logs youtube-competitor-tracker --last 10

### Publish your automation
clawflows publish ./my-automation.yaml

Prints instructions for submitting to the registry via PR.

## How It Works
Automations use **capabilities** (abstract) not skills (concrete):

```yaml
steps:
 - capability: youtube-data # Not a specific skill
 method: getRecentVideos
 args:
 channels: ["@MrBeast"]
 capture: videos

 - capability: database
 method: upsert
 table: videos
 data: "${videos}"

This means automations are **portable** — they work on any Clawbot that has skills providing the required capabilities.

## Standard Capabilities
`youtube-data`, What It Does=Fetch video/channel stats, Example Skills=youtube-api
`database`, What It Does=Store and query data, Example Skills=sqlite-skill
`chart-generation`, What It Does=Create chart images, Example Skills=chart-image
`social-search`, What It Does=Search X/Twitter, Example Skills=search-x
`prediction-markets`, What It Does=Query odds, Example Skills=polymarket
`weather`, What It Does=Get forecasts, Example Skills=weather
`calendar`, What It Does=Read/write events, Example Skills=caldav-calendar
`email`, What It Does=Send/receive email, Example Skills=agentmail
`tts`, What It Does=Text to speech, Example Skills=elevenlabs-tts

## Making Skills ClawFlows-Compatible
To make your skill work with ClawFlows automations, add a `CAPABILITY.md` file:

```markdown

# my-capability Capability
Provides: my-capability
Skill: my-skill

## Methods

### myMethod
**Input:**
- param1: description

**How to fulfill:**
\`\`\`bash
./scripts/my-script.sh --param1 "${param1}"
\`\`\`

**Output:** Description of output format

And declare it in your SKILL.md frontmatter:

name: my-skill
provides:
 - capability: my-capability
 methods: [myMethod]

## Links
- **Registry**: https://clawflows.com
- **CLI on npm**: https://www.npmjs.com/package/clawflows
- **GitHub**: https://github.com/Cluka-399/clawflows-registry