@echo off
set "slugs=claw-shell clawdbot-zoho-email comfy-ai comfyui-runner computer-use deliberate-frontend-redesign discord downloads emporia-energy fanvue frontend-design giphy human-optimized-frontend linux-service-triage miniflux-news nextjs-expert niri-ipc nodetool pinak-frontend-guru react-email-skills remotion-best-practices remotion-server remotion-video-toolkit resume-builder senior-fullstack slack smtp-send technews telegram-reaction-prober trmnl ui-audit ui-design-system ui-skills ui-ux-master ui-ux-pro-max ux-audit ux-decisions ux-researcher-designer vercel-react-best-practices vision-sandbox web-design-guidelines webapp-testing winamp xcodebuildmcp zoho-email-integration"

for %%s in (%slugs%) do (
    echo Installing %%s...
    cmd /c npx clawhub@latest install %%s
)
