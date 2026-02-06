@echo off
git add .
git commit -m "auto-sync: bababot memory update"
if %errorlevel% neq 0 (
    echo Nothing to commit.
) else (
    git push origin main
    echo Sync successful.
)
