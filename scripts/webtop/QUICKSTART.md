# WebTop Local 快速启动指南

## 🚀 一键启动浏览器

```powershell
cd C:\Users\Haide\.openclaw\workspace\scripts\webtop
python webtop_local.py --start
```

**保持运行** - 浏览器启动后会持续运行，其他脚本可以连接使用。

**停止浏览器** - 按 `Ctrl+C` 或运行：
```powershell
python webtop_local.py --stop
```

---

## 📝 在现有脚本中使用

### 修改前（临时浏览器）
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    # ...
    browser.close()  # 关闭后 Cookie 丢失
```

### 修改后（持久化浏览器）
```python
from playwright.sync_api import sync_playwright
from webtop.browser_config import create_browser_context

with sync_playwright() as p:
    browser = create_browser_context(p)  # 连接到持久化浏览器
    page = browser.pages[0] if browser.pages else browser.new_page()
    # ...
    # 不要关闭浏览器！browser.close() 注释掉
```

---

## 🔧 常用命令

| 操作 | 命令 |
|------|------|
| 启动浏览器 | `python webtop_local.py --start` |
| 停止浏览器 | `python webtop_local.py --stop` |
| 查看状态 | `python webtop_local.py --status` |
| 启动监控 | `python webtop_local.py --watchdog` |
| 输出配置 | `python webtop_local.py --config` |

---

## ✅ 部署验证

运行测试：
```powershell
python example_usage.py
```

选择选项 3 查看浏览器配置，确认 CDP 端点可用。

---

## 📂 文件位置

- **脚本**: `scripts/webtop/`
- **浏览器数据**: `C:\Users\Haide\AppData\Local\OpenClaw\BrowserData`
- **状态文件**: `scripts/webtop/webtop-state.json`

---

## 🎯 下一步

1. **启动浏览器**: `python webtop_local.py --start`
2. **手动登录 LinkedIn 和 StockMarket.aero**（首次需要）
3. **更新采集脚本** 使用 `create_browser_context()`
4. **启动 Watchdog**: `python webtop_local.py --watchdog`（后台运行）

完成！🎉
