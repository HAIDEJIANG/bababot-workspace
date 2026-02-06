@echo off
set "list=2captcha abm-outbound activecampaign adcp-advertising Agent-Browser agent-browser agent-zero agentmail-integration apify-lead-generation asr autofillin babyconnect browser-ladder browser-use browsh chirp clawbrowser clawflows context-compressor context-recovery context7 daily-rhythm db-query demo-video fast-browser-use feishu-doc firecrawl-search firecrawl-skills firecrawler gdpr-dsgvo-expert google-web-search guru-mcp hass-cli home-assistant inkedin-automation-that-really-works job-auto-apply kakiyo leadklick mcporter n8n-api n8n-automation n8n-hub newsletter-creation-curation odoo-openclaw-skill organize-tg phantombuster playwright-cli proxy-scrap qiuqiu-helper roon-controller safe-exec sales-bot serper spool stremio-cast tcm-video-factory tekin tiangong-notebooklm-cli tiangong-wps-ppt-automation tiangong-wps-word-automation tinyfish-web-agent turix-computer-use turix-cua verify-on-browser vocal-chat web-qa-bot x-articles xiaohongshu-mcp zellij"

for %%s in (%list%) do (
    echo Installing %%s...
    cmd /c npx clawhub@latest install %%s
)
