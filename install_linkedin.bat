@echo off
set "list=abm-outbound apify-lead-generation inkedin-automation-that-really-works kakiyo job-search-mcp scrappa-skill octolens personal-branding-authority linkdapi multiposting claw-me-maybe linkedin linkedin-cli postiz upload-post"

for %%s in (%list%) do (
    echo Installing %%s...
    cmd /c npx clawhub@latest install %%s
)
