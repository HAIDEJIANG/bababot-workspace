---
name: xiaohongshu-mcp
description: >
 Automate Xiaohongshu (RedNote) content operations using a Python client for the xiaohongshu-mcp server.
 Use for: (1) Publishing image, text, and video content, (2) Searching for notes and trends,
 (3) Analyzing post details and comments, (4) Managing user profiles and content feeds.
 Triggers: xiaohongshu automation, rednote content, publish to xiaohongshu, xiaohongshu search, social media management.

# Xiaohongshu MCP Skill (with Python Client)
Automate content operations on Xiaohongshu (小红书) using a bundled Python script that interacts with the `xpzouying/xiaohongshu-mcp` server (8.4k+ stars).

**Project:** [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)

## 1. Local Server Setup
This skill requires the `xiaohongshu-mcp` server to be running on your local machine.

### Step 1: Download Binaries
Download the appropriate binaries for your system from the [GitHub Releases](https://github.com/xpzouying/xiaohongshu-mcp/releases) page.

macOS (Apple Silicon), MCP Server=`xiaohongshu-mcp-darwin-arm64`, Login Tool=`xiaohongshu-login-darwin-arm64`
macOS (Intel), MCP Server=`xiaohongshu-mcp-darwin-amd64`, Login Tool=`xiaohongshu-login-darwin-amd64`
Windows, MCP Server=`xiaohongshu-mcp-windows-amd64.exe`, Login Tool=`xiaohongshu-login-windows-amd64.exe`
Linux, MCP Server=`xiaohongshu-mcp-linux-amd64`, Login Tool=`xiaohongshu-login-linux-amd64`

Grant execute permission to the downloaded files:
```shell
chmod +x xiaohongshu-mcp-darwin-arm64 xiaohongshu-login-darwin-arm64
```

### Step 2: Login (First Time Only)
Run the login tool. It will open a browser window with a QR code. Scan it with your Xiaohongshu mobile app.

./xiaohongshu-login-darwin-arm64

> **Important**: Do not log into the same Xiaohongshu account on any other web browser, as this will invalidate the server's session.

### Step 3: Start the MCP Server
Run the MCP server in a separate terminal window. It will run in the background.

# Run in headless mode (recommended)
./xiaohongshu-mcp-darwin-arm64

# Or, run with a visible browser for debugging
./xiaohongshu-mcp-darwin-arm64 -headless=false

The server will be available at `http://localhost:18060`.

## 2. Using the Skill
This skill includes a Python client (`scripts/xhs_client.py`) to interact with the local server. You can use it directly from the shell.

### Available Commands
`status`, Description=Check login status, Example=`python scripts/xhs_client.py status`
`search <keyword>`, Description=Search for notes, Example=`python scripts/xhs_client.py search "咖啡"`
`detail <id> <token>`, Description=Get note details, Example=`python scripts/xhs_client.py detail "note_id" "xsec_token"`
`feeds`, Description=Get recommended feed, Example=`python scripts/xhs_client.py feeds`
`publish <title> <content> <images>`, Description=Publish a note, Example=`python scripts/xhs_client.py publish "Title" "Content" "url1,url2"`

### Example Workflow: Market Research
1. **Check Status**: First, ensure the server is running and you are logged in.
 python ~/clawd/skills/xiaohongshu-mcp/scripts/xhs_client.py status

2. **Search for a Keyword**: Find notes related to your research topic. The output will include the `feed_id` and `xsec_token` needed for the next step.
 python ~/clawd/skills/xiaohongshu-mcp/scripts/xhs_client.py search "户外电源"

3. **Get Note Details**: Use the `feed_id` and `xsec_token` from the search results to get the full content and comments of a specific note.
 python ~/clawd/skills/xiaohongshu-mcp/scripts/xhs_client.py detail "64f1a2b3c4d5e6f7a8b9c0d1" "security_token_here"

4. **Analyze**: Review the note's content, comments, and engagement data to gather insights.