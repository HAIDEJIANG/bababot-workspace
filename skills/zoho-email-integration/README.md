# Zoho Email Integration for Clawdbot
[![GitHub](https://img.shields.io/badge/GitHub-clawdbot--zoho--email-blue?logo=github)](https://github.com/briansmith80/clawdbot-zoho-email)
[![ClawdHub](https://img.shields.io/badge/ClawdHub-Install-green)](https://clawdhub.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.2-blue)](https://github.com/briansmith80/clawdbot-zoho-email/releases)

**v2.0.2** - Complete Zoho Mail integration with OAuth2, REST API backend (5-10x faster), and advanced email automation features. Perfect for email workflows, monitoring, and bulk operations in your Clawdbot projects.

## Quick Start (recommended path)
```bash

# 1) Install
clawdhub install zoho-email
cd zoho-email # (or wherever ClawdHub installed it)

# 2) Install Python deps (needed for REST API mode)
pip3 install -r requirements.txt

# 3) Set your mailbox (required for both OAuth + app-password modes)
export ZOHO_EMAIL="your-email@domain.com"

# 4) OAuth2 setup (recommended: enables REST API + auto token refresh)
python3 scripts/oauth-setup.py

# 5) Sanity-check everything
python3 scripts/zoho-email.py doctor

# 6) Test
python3 scripts/zoho-email.py unread
```

### Quick Start (app-password mode)
If you don't want OAuth2 yet:

export ZOHO_PASSWORD="your-app-specific-password"
python3 scripts/zoho-email.py unread --api-mode imap

**OAuth token location (default):** `~/.clawdbot/zoho-mail-tokens.json`

## Features

### Core Features
**OAuth2 Authentication** - Secure authentication with automatic token refresh
 **REST API Backend** - 5-10x faster than IMAP/SMTP (auto-enabled with OAuth2)
 **Read & Search** - Search emails with advanced filters
 **Send Emails** - Plain text, HTML, CC/BCC support
 **Attachments** - Send and download attachments
 **HTML Emails** - Send rich-formatted emails with templates
 **Batch Operations** - Mark, delete, move multiple emails efficiently
 **Folder Management** - Access all folders (Inbox, Sent, Drafts, etc.)

### Performance
**5-10x faster** operations with REST API mode
 **Connection pooling** for persistent HTTP connections
 **Server-side filtering** reduces data transfer
 **Automatic fallback** to IMAP if REST API unavailable

## Documentation
- **[SKILL.md](SKILL.md)** - Complete guide with examples
- **[OAUTH2_SETUP.md](OAUTH2_SETUP.md)** - OAuth2 setup instructions
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

# Search inbox
python3 scripts/zoho-email.py search "invoice"

# Read a specific email (folder + id)
python3 scripts/zoho-email.py get INBOX <id>

# Send a simple email
python3 scripts/zoho-email.py send recipient@example.com "Subject" "Body text"

# Empty Spam (safe by default: DRY RUN)
python3 scripts/zoho-email.py empty-spam

# Execute for real
python3 scripts/zoho-email.py empty-spam --execute

# Empty Trash (safe by default: DRY RUN)
python3 scripts/zoho-email.py empty-trash
python3 scripts/zoho-email.py empty-trash --execute

# Search emails
python3 scripts/zoho-email.py search "important meeting"

# Send email
python3 scripts/zoho-email.py send recipient@example.com "Subject" "Message body"

# Send HTML email from template
python3 scripts/zoho-email.py send-html user@example.com "Newsletter" templates/newsletter.html

# Preview HTML before sending
python3 scripts/zoho-email.py preview-html templates/welcome.html

# Send with attachments
python3 scripts/zoho-email.py send user@example.com "Report" "See attached" --attach report.pdf --attach data.xlsx

# List attachments in an email
python3 scripts/zoho-email.py list-attachments Inbox 4590

# Download attachment
python3 scripts/zoho-email.py download-attachment Inbox 4590 0 ./report.pdf

# Mark multiple emails as read
python3 scripts/zoho-email.py mark-read INBOX 1001 1002 1003

# Delete multiple emails (with confirmation)
python3 scripts/zoho-email.py delete INBOX 2001 2002 2003

# Move emails to folder
python3 scripts/zoho-email.py move INBOX "Archive/2024" 3001 3002

# Bulk action with search
python3 scripts/zoho-email.py bulk-action \
 --folder INBOX \
 --search 'SUBJECT "newsletter"' \
 --action mark-read \
 --dry-run

# Check OAuth2 status
python3 scripts/zoho-email.py oauth-status

# Force REST API mode (5-10x faster)
python3 scripts/zoho-email.py unread --api-mode rest --verbose

# Force IMAP mode (compatibility)

## Clawdbot command wrapper (optional)
If you want a simple "command-style" wrapper script for Clawdbot (e.g., `/emails`), see:

- `examples/clawdbot-commands/emails.sh`

It's intentionally minimal and safe (dry-run by default for destructive actions).

## Use Cases
- **Morning briefings** - Automated unread email summaries
- **Email monitoring** - Watch for VIP senders or keywords
- **Newsletter cleanup** - Bulk-mark newsletters as read
- **Automated responses** - Search and reply to specific emails
- **Email archiving** - Move old emails to archive folders
- **Notifications** - Alert when important emails arrive
- **HTML campaigns** - Send rich-formatted newsletters
- **Attachment workflows** - Download invoices, reports automatically

## Requirements
**Minimum:**
- Python 3.x
- Zoho Mail account
- App-specific password OR OAuth2 setup

**Optional (for REST API mode):**
- `requests>=2.31.0` (install: `pip3 install -r requirements.txt`)
- OAuth2 credentials (automatic 5-10x performance boost)

## Version History
- **v2.0.0** (2025-01-29) - REST API backend with 5-10x performance boost
- **v1.2.0** (2025-01-29) - OAuth2 authentication with automatic token refresh
- **v1.1.0** (2025-01-29) - HTML emails, attachments, batch operations
- **v1.0.0** (2025-01-29) - Initial IMAP/SMTP implementation

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## Contributing
Contributions are welcome! Here's how you can help:

- **Request features:** [Open an issue](https://github.com/briansmith80/clawdbot-zoho-email/issues)
- **Submit PRs:** [Pull requests](https://github.com/briansmith80/clawdbot-zoho-email/pulls)
- ⭐ **Star the repo:** Show your support!

This is an open-source Clawdbot skill maintained by the community.

## License
MIT License - see [LICENSE](LICENSE) for details.

---

**Part of the Clawdbot ecosystem** | [ClawdHub](https://clawdhub.com) | [Documentation](SKILL.md)