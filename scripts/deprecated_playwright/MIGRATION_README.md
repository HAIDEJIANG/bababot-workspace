# Playwright 脚本归档目录

## 归档时间
2026-03-30

## 归档原因
- Playwright 及其浏览器组件已卸载
- 改用纯 CDP 协议方案（linkedin_v9_cdp.py）
- 减少依赖，提高稳定性

## 已归档脚本
| 脚本名称 | 原用途 | 替代方案 |
|---------|--------|---------|
| linkedin_collection_v4_webtop.py | WebTop 持久化浏览器采集 | linkedin_v9_cdp.py |
| linkedin_feed_optimized.py | Feed 优化采集 | linkedin_v9_cdp.py |
| linkedin_feed_quick.py | Feed 快速采集 | linkedin_v9_cdp.py |
| linkedin_feed_simple.py | Feed 简单采集 | linkedin_v9_cdp.py |
| linkedin_feed_v2.py | Feed v2 采集 | linkedin_v9_cdp.py |
| linkedin_feed_v3.py | Feed v3 采集 | linkedin_v9_cdp.py |
| linkedin_v5_headless.py | 无头模式采集 | linkedin_v9_cdp.py |
| linkedin_v6_stealth.py | Stealth 模式采集 | linkedin_v9_cdp.py |
| linkedin_quick_collect.py | 快速采集 | linkedin_v9_cdp.py |
| export_cookies.py | Cookie 导出 | 不再需要（CDP 直接复用浏览器 Cookie） |
| setup_linkedin_cli_env.py | CLI 环境设置 | 不再需要 |
| open_browser_for_login.py | 打开浏览器登录 | 手动启动 Edge 带调试端口 |

## 新方案优势
1. **零 Playwright 依赖** - 仅使用标准库 + websocket-client + requests
2. **更轻量** - 无需下载 Chromium 等浏览器二进制文件
3. **Cookie 自动复用** - 直接连接已登录的 Edge 浏览器
4. **更易维护** - 代码简单，调试方便

## 如何使用新脚本
```powershell
# 1. 确保 Edge 已启动并开启远程调试端口
# 首次启动命令：
Start-Process "msedge" -ArgumentList "--remote-debugging-port=9222","--user-data-dir=C:\Users\Haide\AppData\Local\Microsoft\Edge\User Data\OpenClawProfile"

# 2. 在 Edge 中访问 LinkedIn 并登录
# https://www.linkedin.com/feed

# 3. 运行采集脚本
python scripts/linkedin_v9_cdp.py --duration 30

# 4. 查看输出
# CSV: C:\Users\Haide\Desktop\real business post\linkedin_posts_YYYYMMDD_HHMMSS.csv
# JSON: C:\Users\Haide\Desktop\real business post\linkedin_posts_YYYYMMDD_HHMMSS.json
```

## Cron 自动任务
已更新：`.openclaw/cron/jobs/linkedin-auto-collection.json`
- 脚本：linkedin_v9_cdp.py
- 频率：每 4 小时
- 时长：30 分钟
- 状态：✅ 已启用

## 恢复旧脚本（如需）
```powershell
# 如需恢复某个旧脚本，复制回 scripts 目录即可
Copy-Item "deprecated_playwright\linkedin_collection_v4_webtop.py" "scripts\"
```

## 依赖安装
```powershell
# 新脚本所需依赖（已安装）
pip install websocket-client requests
```

---
**迁移完成时间**: 2026-03-30
**负责人**: bababot
