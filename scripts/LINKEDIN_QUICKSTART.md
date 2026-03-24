# LinkedIn 自动采集系统 - 快速启动指南

## 🚀 一键启动（推荐）

### 步骤 1: 启动持久化浏览器
`powershell
python scripts/webtop/webtop_local.py --start
`

### 步骤 2: 登录 LinkedIn（首次需要）
在打开的浏览器中手动登录 LinkedIn 账号

### 步骤 3: 运行采集
`powershell
python scripts/linkedin_collection_v4_webtop.py
`

---

## 📅 自动化配置

### Cron 定时任务（已配置）
- **频率**: 每 4 小时执行一次
- **时间窗口**: 08:00-23:00
- **命令**: python scripts/linkedin_collection_v4_webtop.py --auto
- **配置文件**: .openclaw/cron/jobs/linkedin-auto-collection.json

### 启用 Cron 任务
`powershell
openclaw cron enable linkedin-auto-collection
`

### 查看 Cron 状态
`powershell
openclaw cron list
`

---

## 🛡️ 监控与告警

### 启动 Watchdog 监控
`powershell
python scripts/webtop/browser_watchdog.py start
`

### Watchdog 功能
- ✅ 每 60 秒检查浏览器健康状态
- ✅ 浏览器无响应时自动重启
- ✅ 记录详细日志
- ✅ 支持 Telegram 告警（配置后）

---

## 📊 数据输出

### 采集结果位置
`
C:\Users\Haide\Desktop\real business post\
├── LinkedIn_Business_Posts_Master_Table.csv  # 总表
├── linkedin_posts_YYYY-MM-DD.json           # 每日原始数据
└── collection_log.txt                        # 采集日志
`

### 数据格式
每条记录包含：
- 发帖人姓名、公司、职务
- 联系方式（Email/Phone/WhatsApp）
- 帖子内容、发布时间
- 帖子链接（Raw Text URL）
- 采集时间、使用的账号

---

## 🔧 常用命令

### 浏览器管理
`powershell
# 启动浏览器
python scripts/webtop/webtop_local.py --start

# 停止浏览器
python scripts/webtop/webtop_local.py --stop

# 清除缓存
python scripts/webtop/webtop_local.py --clear-cache

# 查看状态
python scripts/webtop/webtop_local.py --status
`

### Cookie 管理
`powershell
# 导出 Cookie
python scripts/cookie_manager.py export

# 导入 Cookie
python scripts/cookie_manager.py import

# 查看 Cookie 数量
python scripts/cookie_manager.py status
`

### 采集控制
`powershell
# 运行采集（默认 60 分钟）
python scripts/linkedin_collection_v4_webtop.py

# 运行采集（指定时长 30 分钟）
python scripts/linkedin_collection_v4_webtop.py --duration 30

# 运行采集（指定条数 50 条）
python scripts/linkedin_collection_v4_webtop.py --limit 50

# 后台运行
python scripts/linkedin_collection_v4_webtop.py --auto
`

---

## 🎯 最佳实践

### 每日检查（08:00-23:00）
1. 检查浏览器进程是否运行
2. 查看前一日采集数据质量
3. 监控账号使用频率
4. 检查 Master Table 更新

### 每周维护
1. 重新导出 Cookie（确保新鲜度）
2. 清理浏览器缓存
3. 审查被过滤的帖子（调整关键词）
4. 备份 Master Table 到 GitHub

### 故障处理
遇到问题时的检查顺序：
1. 浏览器进程是否运行？
2. Cookie 是否有效？
3. 网络连接是否正常？
4. LinkedIn 是否可手动访问？
5. 查看日志文件定位错误

---

## 📞 支持

### 日志文件位置
`
logs/
├── browser_manager.log      # 浏览器管理日志
├── linkedin_collection.log  # 采集日志
├── watchdog.log            # 监控日志
└── cookie_rotation.log     # Cookie 轮换日志
`

### 文档位置
- 完整流程文档：scripts/LINKEDIN_AUTO_COLLECTION.md
- WebTop 部署指南：scripts/webtop/README.md
- 快速启动指南：scripts/LINKEDIN_QUICKSTART.md（本文档）

---

**最后更新**: 2026-03-24 11:00 GMT+8
**版本**: v7.0
