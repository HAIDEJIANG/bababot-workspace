# 浏览器配置说明

## 默认浏览器：Microsoft Edge

**原因**: Chrome 已卸载，Edge 基于 Chromium 内核，兼容性相同

## Edge 配置

### CDP 调试端口
```
--remote-debugging-port=9222
```

### 启动命令（一次性设置）
```powershell
# 关闭所有 Edge 实例
Stop-Process -Name msedge -Force -ErrorAction SilentlyContinue

# 启动 Edge 带远程调试端口（必须包含 remote-allow-origins）
Start-Process "msedge" -ArgumentList @(
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    "--user-data-dir=C:\Users\Haide\AppData\Local\Microsoft\Edge\User Data\OpenClawProfile",
    "--no-first-run"
)
```

**⚠️ 重要**: 必须添加 `--remote-allow-origins=*` 参数，否则 WebSocket 连接会被拒绝 (403 Forbidden)

### 或使用快捷方式
目标路径添加参数：
```
"msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\Haide\AppData\Local\Microsoft\Edge\User Data\OpenClawProfile"
```

## 使用方式

### 方案 A: CDP 协议直连（推荐 - v9 脚本）
```python
from cdp_client import CDPClient

client = CDPClient(port=9222)
tabs = client.get_browser_tabs()
linkedin_tab = client.find_linkedin_feed()
client.connect(linkedin_tab['webSocketDebuggerUrl'])
posts = client.extract_posts()
```
- ✅ 无需 Playwright
- ✅ 使用标准库 + websocket-client
- ✅ Cookie 自动复用（浏览器已登录状态）
- ✅ 轻量级，依赖少

### 方案 B: Selenium（备选）
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Edge(options=options)
```

## 首次使用
1. 启动 Edge 带远程调试端口（见上方命令）
2. 访问 https://www.linkedin.com/feed 并登录
3. Cookie 永久保存到用户数据目录
4. 下次无需重新登录

## 运行采集脚本
```powershell
# 基础用法
python scripts/linkedin_v9_cdp.py --duration 30

# 指定端口
python scripts/linkedin_v9_cdp.py --duration 60 --port 9222

# 查看帮助
python scripts/linkedin_v9_cdp.py --help
```

## 注意事项
- 确保 Edge 已启动并开启远程调试端口
- 首次需要手动登录 LinkedIn
- 登录后 Cookie 永久保存
- 采集时保持 Edge 运行状态
- 不要关闭调试端口所在的浏览器实例

## 依赖安装
```powershell
# CDP 客户端依赖（已安装）
pip install websocket-client requests
```

---
**更新时间**: 2026-03-30
**更新原因**: Playwright 已卸载，改用纯 CDP 协议方案
