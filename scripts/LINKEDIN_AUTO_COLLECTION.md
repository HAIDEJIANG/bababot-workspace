# LinkedIn 自动采集流程 v7.0

## 📋 系统架构

\\\
┌─────────────────────────────────────────────────────────────┐
│                    LinkedIn 采集系统 v7.0                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  WebTop      │  │  Browser     │  │  Watchdog    │       │
│  │  持久化浏览器  │  │  Relay 备用  │  │  监控守护     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │  Cookie 管理器   │                        │
│                  │  (25 个账号池)    │                        │
│                  └────────┬────────┘                        │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │  采集脚本 v4.x   │                        │
│                  │  (有头+Stealth)  │                        │
│                  └────────┬────────┘                        │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │  数据去重汇总    │                        │
│                  │  (Master Table) │                        │
│                  └─────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
\\\

---

## 🗂️ 文件结构

\\\
C:\Users\Haide\.openclaw\workspace\
├── scripts/
│   ├── webtop/
│   │   ├── webtop_local.py         # WebTop 浏览器启动脚本
│   │   ├── browser_config.py       # 浏览器配置
│   │   ├── browser_watchdog.py     # 监控守护进程
│   │   └── example_usage.py        # 使用示例
│   ├── linkedin_collection_v4_webtop.py  # 主采集脚本（推荐）
│   ├── linkedin_simple_v41.py            # 简化版采集
│   ├── linkedin_v5_headless.py           # 无头模式（备用）
│   ├── linkedin_v6_stealth.py            # Stealth 无头（备用）
│   ├── cookie_manager.py                 # Cookie 导出/导入工具
│   ├── export_cookies.py                 # Cookie 导出脚本
│   ├── linkedin_cookies.json             # Cookie 池
│   └── LINKEDIN_AUTO_COLLECTION.md       # 本文档
├── Desktop/
│   └── real business post/
│       └── LinkedIn_Business_Posts_Master_Table.csv  # 总表
└── .openclaw/cron/jobs/
    └── linkedin-auto-collection.json  # Cron 配置
\\\

---

## ⚙️ 核心配置

### 1. WebTop 持久化浏览器

**启动命令:**
\\\ash
python scripts/webtop/webtop_local.py --start
\\\

**参数说明:**
- \--start\: 启动持久化浏览器
- \--port 9222\: Chrome DevTools 端口（默认）
- \--user-data-dir\: 用户数据目录（持久化 Cookie）

**优势:**
- ✅ Cookie 永久保存，无需反复登录
- ✅ 多脚本共享浏览器会话
- ✅ 可见窗口，最难被检测

### 2. Cookie 管理

**导出 Cookie:**
\\\ash
python scripts/cookie_manager.py export
\\\

**导入 Cookie:**
\\\ash
python scripts/cookie_manager.py import
\\\

**Cookie 池轮换策略:**
- 每次采集使用不同账号
- 单账号每日最多采集 50 次
- 自动检测 Cookie 过期并标记

### 3. 采集脚本（推荐顺序）

**首选：v4_webtop 版本**
\\\ash
python scripts/linkedin_collection_v4_webtop.py
\\\

**简化版：v41**
\\\ash
python scripts/linkedin_simple_v41.py
\\\

**备用：v6_stealth**
\\\ash
python scripts/linkedin_v6_stealth.py
\\\

---

## 🔄 自动化流程

### 方案 A: WebTop + 采集脚本（推荐⭐）

\\\
1. 启动持久化浏览器
   → python scripts/webtop/webtop_local.py --start

2. 手动登录 LinkedIn（首次需要）
   → 在打开的浏览器中登录

3. 运行采集脚本
   → python scripts/linkedin_collection_v4_webtop.py

4. 导出数据
   → 自动追加到 Master Table

5. 保持浏览器后台运行（可选）
   → 下次无需重新登录
\\\

**优点:**
- ✅ Cookie 持久化，无需重复登录
- ✅ 可见窗口，最稳定
- ✅ 可人工辅助滚动触发内容

**缺点:**
- 需要可见窗口
- 需要首次手动登录

### 方案 B: Browser Relay（备用）

当 WebTop 方案不可用时：

\\\
1. 手动打开 Chrome，登录 LinkedIn
2. 点击 Browser Relay 扩展图标（龙虾）
3. 运行采集命令
   → openclaw browser act ...
\\\

**优点:**
- ✅ 使用用户真实浏览器
- ✅ 最难被检测

**缺点:**
- 需要手动操作
- 不适合完全自动化

---

## 📊 数据采集标准

### 关键词策略

**广域关键词（OR 逻辑）:**
\\\
Aircraft OR Engine OR "Spare parts" OR "Aviation components" 
OR "Landing Gear" OR APU OR CFM56 OR V2500 OR PW4000 
OR LEAP OR Trent OR A320 OR B737 OR B777 OR A350
\\\

**过滤规则:**
- ❌ 排除：行业新闻、会议通知、公关稿、招聘
- ✅ 保留：含 PN 号、S/N、价格、联系方式、买卖意图

### 输出格式

每条记录包含：
| 字段 | 说明 |
|------|------|
| 发帖人姓名 | Full Name |
| 公司名 | Company |
| 职务 | Title |
| 联系方式 | Email/Phone/WhatsApp |
| 发帖时间 | ISO 8601 |
| 帖子内容 | 纯文本 |
| 帖子链接 | Raw Text URL（code block 格式） |
| 采集时间 | Timestamp |
| 账号 ID | 使用的 Cookie 账号 |

---

## 🛡️ 反检测策略

### 1. 浏览器指纹
- ✅ 随机 User-Agent（每会话轮换）
- ✅ 随机屏幕分辨率
- ✅ 随机时区设置
- ✅ WebGL 指纹模糊化

### 2. 行为模拟
- ✅ 随机滚动速度（50-200ms/像素）
- ✅ 随机停留时间（2-8 秒/帖子）
- ✅ 模拟鼠标移动轨迹
- ✅ 偶尔点击（点赞/评论）

### 3. 请求频率
- 单账号：最多 50 次/天
- 每次采集间隔：30-120 秒
- 账号轮换：每 10 次请求换账号
- 夜间静默：23:00-08:00 不采集

### 4. Cookie 管理
- 25 个账号池轮换
- 自动检测过期 Cookie
- 定期更新（每周重新导出）
- 备用账号随时待命

---

## 🔧 故障处理

### 问题 1: Feed 无法加载
**症状:** 页面空白或无限加载

**解决方案:**
\\\ash
# 1. 清除浏览器缓存
python scripts/webtop/webtop_local.py --clear-cache

# 2. 重新登录
手动打开浏览器，登录 LinkedIn

# 3. 重新导出 Cookie
python scripts/cookie_manager.py export

# 4. 切换账号
python scripts/linkedin_collection_v4_webtop.py --account-index 1
\\\

### 问题 2: 被 LinkedIn 检测
**症状:** 弹出验证码或账号限制

**解决方案:**
\\\ash
# 1. 立即停止采集
# 2. 切换账号（使用未受限账号）
# 3. 降低采集频率（--delay 参数增加到 120 秒）
# 4. 使用 Browser Relay 备用方案
\\\

### 问题 3: Browser Relay 断开
**症状:** 龙虾图标变灰，无法附加

**解决方案:**
\\\ash
# 1. 检查扩展是否启用
chrome://extensions → 找到 OpenClaw Browser Relay → 启用

# 2. 重新附加
点击龙虾图标 → Attach Tab

# 3. 自动重连已启用（background.js 已 patched）
\\\

---

## 📈 监控与日志

### Watchdog 监控

**启动监控:**
\\\ash
python scripts/webtop/browser_watchdog.py start
\\\

**监控内容:**
- 浏览器进程状态
- Cookie 有效性
- 采集脚本运行状态
- 网络连通性

**告警方式:**
- 本地日志文件
- Telegram 推送（配置后）
- 自动重启失败进程

### 日志文件

\\\
logs/
├── browser_manager.log      # 浏览器管理日志
├── linkedin_collection.log  # 采集日志
├── watchdog.log            # 监控日志
└── cookie_rotation.log     # Cookie 轮换日志
\\\

---

## 🎯 最佳实践

### 日常运维清单

**每日 (08:00-23:00):**
- [ ] 检查浏览器进程是否运行
- [ ] 查看前一日采集数据质量
- [ ] 监控账号使用频率
- [ ] 检查 Master Table 更新

**每周:**
- [ ] 重新导出 Cookie（确保新鲜度）
- [ ] 清理浏览器缓存
- [ ] 审查被过滤的帖子（调整关键词）
- [ ] 备份 Master Table 到 GitHub

**每月:**
- [ ] 评估账号健康状态
- [ ] 更新 User-Agent 池
- [ ] 优化反检测策略
- [ ] 汇总业务线索数量

### 性能优化

**采集速度:**
- 理想状态：30 条/小时（高质量）
- 快速模式：60 条/小时（需降低质量检查）
- 保守模式：15 条/小时（最安全）

**去重效率:**
- 基于帖子哈希值去重
- 基于 URL 去重
- 基于内容相似度去重（95% 阈值）

---

## 🚀 快速启动

### 首次设置
\\\ash
# 1. 安装依赖
pip install playwright python-dotenv pandas

# 2. 安装浏览器
playwright install chrome

# 3. 启动浏览器
python scripts/webtop/webtop_local.py --start

# 4. 手动登录 LinkedIn（在打开的浏览器中）

# 5. 导出 Cookie
python scripts/cookie_manager.py export

# 6. 运行采集
python scripts/linkedin_collection_v4_webtop.py
\\\

### 日常使用
\\\ash
# 一键采集（假设浏览器已在运行）
python scripts/linkedin_collection_v4_webtop.py --auto
\\\

---

## 📞 支持

遇到问题时的检查顺序：
1. 浏览器进程是否运行？
2. Cookie 是否有效？
3. 网络连接是否正常？
4. LinkedIn 是否可手动访问？
5. 查看日志文件定位错误

---

## 📝 版本历史

- **v7.0 (2026-03-24)**: 整合 WebTop + Cookie 池 + Watchdog
- **v6.0 (2026-03-23)**: Stealth 无头模式（失败，Feed 无法加载）
- **v5.0 (2026-03-23)**: 无头模式（失败，Feed 无法加载）
- **v4.1 (2026-03-22)**: 有头+Stealth（成功，重复率 98%）
- **v4.0 (2026-03-24)**: WebTop 持久化浏览器版（当前推荐）

---

**最后更新:** 2026-03-24 10:56 GMT+8

**下一步计划:**
1. ✅ 文档创建完成
2. ⏳ 配置 Cron 定时任务（每 4 小时自动采集）
3. ⏳ 设置 Watchdog 自动监控
4. ⏳ 配置 Telegram 告警推送
