# 浏览器配置说明

## 默认浏览器：Microsoft Edge

**原因**: Chrome 已卸载，Edge 基于 Chromium 内核，兼容性相同

## Edge 配置

### 用户数据目录
```
C:\Users\Haide\AppData\Local\Microsoft\Edge\User Data\OpenClawProfile
```

### CDP 调试端口
```
--remote-debugging-port=9224
```

### 启动参数
```python
args=[
    "--remote-debugging-port=9224",
    "--disable-blink-features=AutomationControlled",
]
```

## 使用方式

### 方案 A: OpenClaw Browser 工具（推荐）
```python
browser.action = "navigate"
browser.url = "https://www.linkedin.com/feed/"
```
- ✅ 自动使用 Edge
- ✅ Cookie 自动保存
- ✅ 无需手动配置

### 方案 B: Playwright 直接连接
```python
context = p.chromium.launch_persistent_context(
    user_data_dir=r"C:\Users\Haide\AppData\Local\Microsoft\Edge\User Data\OpenClawProfile",
    headless=False,
    args=["--remote-debugging-port=9224"],
)
```

## 首次使用
1. 运行脚本会自动打开 Edge
2. 访问 LinkedIn 并登录
3. Cookie 永久保存到用户数据目录
4. 下次无需重新登录

## 注意事项
- Edge 和 Chrome 的 Cookie 不互通
- 首次需要重新登录 LinkedIn
- 登录后 Cookie 永久保存

---
**更新时间**: 2026-03-29
**更新原因**: Chrome 已卸载，改用 Edge
