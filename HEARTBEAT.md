# HEARTBEAT.md - Automated Tasks
This file defines periodic tasks that should run during heartbeat checks.

---

## 心跳配置说明 (根据 OpenClaw 最佳实践)

**活动时间窗口**: 08:00-23:00（夜间自动跳过，节省 token）
**心跳间隔**: 30 分钟
**告警**: 已启用（异常情况主动推送）
**记忆保护**: 压缩前自动落盘（防止关键信息丢失）

---

## 心跳检查规则

### 夜间静默规则 (23:00-08:00)
- ❌ 跳过常规巡检
- ✅ 仅处理紧急告警
- ✅ 记录心跳状态但不执行任务

### 日间巡检规则 (08:00-23:00)
- ✅ 每 30 分钟执行一次
- ✅ 正常时静默 (HEARTBEAT_OK)
- ✅ 异常时主动告警

---

## Unified Heartbeat Check (optimized)

Run the following during each heartbeat (single exec call for all checks):

```powershell
python .\scripts\heartbeat_optimized.py
```

This unified script performs:
1. Memory compression (benchmark + compress + dict + observe)
2. System status check (git status, subagents, health)
3. **Active task progress check** (detect stalled tasks)
4. **Auto-restart failed tasks** (with user notification)
5. Evolver safety review (review mode)
6. Automatic report generation

All results are saved to `memory/heartbeat_report.md`.

### Task Monitoring Rules:
- Check active tasks every heartbeat (every 10 minutes)
- If task progress unchanged for >30 minutes → auto-restart
- If script crashes → log error + notify user + restart with fallback script
- Track task health in `memory/task_progress.json`

## Weekly Maintenance Tasks

### LinkedIn 自动采集（Cron 自动执行 - 每 4 小时）
- **周二 - 周六**: 采集 LinkedIn Feed 信息流
- **周日 - 周一**: 采集已加入的 LinkedIn 群组
- 更新总表：`~/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv`
- Cron 配置：`~/.openclaw/cron/jobs/linkedin-auto-collection.json`

[ ] Run full memory compression (full command)
[ ] Check for duplicate entries (dedup command)
[ ] Update MEMORY.md with significant events from daily notes
[ ] Clean old observation files if older than 30 days

## Daily Quick Checks (rotate through these)
Email inbox (if configured)
Calendar for upcoming events (< 24h)
Weather (if relevant)
Git status in workspace (using layered reporting)

Run unified system status check (recommended - combines multiple checks):
```powershell
python .\scripts\system_status_check.py
```

Or run layered git status separately:
```powershell
python .\scripts\git_status_layered.py
```

## Evolver Safety Run (review mode)
Run once per day (or every 12h max) as a low-risk review cycle:

```powershell
cd .\skills\evolver
node index.js run --review
```

Expected behavior for this version:
- Generates a GEP prompt and prints a `sessions_spawn(...)` suggestion
- Does not auto-apply code changes by itself in this step

If output indicates major file edits or unclear behavior:
- Stop and notify the user for approval before any follow-up action.

## Notes
Compression is lossless for rules/dict/RLE, lossy but fact-preserving for observations
Keep .codebook.json with memory files — required for decompression
Run install command to re-install this heartbeat entry if needed:
 python scripts/mem_compress.py .. install