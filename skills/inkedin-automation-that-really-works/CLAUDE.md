# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Python-based LinkedIn automation tool using Playwright for headless browser automation. CLI entry point at `scripts/linkedin.py` with modular library in `scripts/lib/`.

## Setup & Commands
```bash

# Install
python3 -m pip install playwright
playwright install chromium

# Verify session
python3 scripts/linkedin.py check-session

# Read-only commands
python3 scripts/linkedin.py feed --count 5
python3 scripts/linkedin.py analytics --count 10
python3 scripts/linkedin.py profile-stats
python3 scripts/linkedin.py scan-likes --count 15
python3 scripts/linkedin.py get-style
python3 scripts/linkedin.py activity --profile-url <URL> --count 5

# Write commands (require explicit user approval)
python3 scripts/linkedin.py post --text "Content"
python3 scripts/linkedin.py comment --url <URL> --text "Comment"
python3 scripts/linkedin.py edit-comment --url <URL> --match "old" --text "new"
python3 scripts/linkedin.py delete-comment --url <URL> --match "text"
python3 scripts/linkedin.py repost --url <URL> --thoughts "Take"

# Debug mode
LINKEDIN_DEBUG=1 python3 scripts/linkedin.py <command>
```

No test suite exists. No linter configured.

## Architecture
- **`scripts/linkedin.py`** — CLI dispatcher with argparse
- **`scripts/lib/selectors.py`** (442 lines) — Core resilience layer. Multi-strategy fallback selector engine that tries multiple CSS/attribute/JS selectors per DOM element. This is the most complex module and the first place to look when LinkedIn UI changes break functionality.
- **`scripts/lib/actions.py`** — Post/comment/edit/delete/repost with @mention support via typeahead dropdown simulation
- **`scripts/lib/browser.py`** — Playwright lifecycle with persistent profile at `~/.linkedin-browser`, headless by default, German locale
- **`scripts/lib/analytics.py`** — Engagement stats scraping
- **`scripts/lib/feed.py`** — Feed reading via JS evaluation
- **`scripts/lib/like_monitor.py`** — Reaction tracking with state persistence at `~/.linkedin-likes-state.json`
- **`scripts/lib/style_learner.py`** — Voice/tone profile extraction stored at `~/.linkedin-style.json`
- **`scripts/lib/profile.py`** — Profile activity scraping

## Key Design Decisions
- **Selector resilience**: Every DOM lookup uses ordered fallback strategies (CSS, attributes, JS evaluation). When LinkedIn changes their UI, add new selectors to the fallback chain in `selectors.py` rather than replacing existing ones.
- **@Mention flow**: Regex detects `@First Last`, types into LinkedIn typeahead, completes letter-by-letter. Falls back to plain text on failure.
- **All output is JSON** to stdout. Debug screenshots go to `/tmp/linkedin_debug_*.png`.
- **Golden rule**: NEVER post, comment, repost, edit, or delete without explicit user approval. Read-only operations are safe to run freely.

## Environment Variables
`LINKEDIN_BROWSER_PROFILE`, Default=`~/.linkedin-browser`, Purpose=Persistent browser profile path
`LINKEDIN_DEBUG`, Default=unset, Purpose=Enable debug logging (set to `1`)
`LINKEDIN_LIKES_STATE`, Default=`~/.linkedin-likes-state.json`, Purpose=Like monitor state file
`LINKEDIN_STYLE_FILE`, Default=`~/.linkedin-style.json`, Purpose=Learned voice profile

## Reference Documents
`references/content-strategy.md`, `references/engagement.md`, and `references/dom-patterns.md` contain LinkedIn algorithm insights, posting guidelines, rate limits, and known DOM patterns for troubleshooting.