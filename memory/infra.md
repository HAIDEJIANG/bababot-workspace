# 基础设施配置速查 (Infrastructure)
**更新时间**: 2026-03-19
**用途**: 服务器,API,部署等配置速查

---

## OpenClaw 环境

### 运行时信息
- **Runtime**: agent=main | host=DESKTOP-7S7DDHL
- **Repo**: `C:\Users\Haide\.openclaw\workspace`
- **OS**: Windows_NT 10.0.26200 (x64)
- **Node**: v24.13.0, **默认 Model**: bailian/qwen3.5-plus, **Shell**: powershell, **当前 Channel**: telegram

### 时区
- **主时区**: Asia/Hong_Kong
- **备用**: Asia/Shanghai

## 已配置渠道

### Telegram
- **状态**: 已启用, **Chat ID**: telegram:1953617060, **Account**: default, **功能**: inlineButtons 支持

### Discord
- **状态**: ⏸️ 未启用
- **待配置**: MESSAGE CONTENT INTENT

## 已安装 Skills

### 核心 Skills
- weather - 天气查询
- github - GitHub 操作
- browser - 浏览器自动化,browser-use - 浏览器交互,scrapling-scraper - 网页抓取
- pdf - PDF 处理
- email-daily-summary - 邮件摘要
- imap-smtp-email - IMAP/SMTP 邮件
- linkedin-automator - LinkedIn 自动化
- linkedin-cli - LinkedIn CLI
- safe-exec - 安全命令执行
- self-improvement - 自我改进

### 工作流 Skills
- executing-plans - 执行计划,finishing-a-development-branch - 完成开发分支,requesting-code-review - 请求代码审查
- dispatching-parallel-agents - 并行 Agent 调度

### 系统 Skills
- healthcheck - 健康检查
- node-connect - 节点连接诊断
- skill-creator - Skill 创建
- clawhub - Skill 市场
- mcporter - MCP 服务器

## 自动化配置

### Heartbeat
- **Prompt**: 读取 HEARTBEAT.md,执行周期性任务
- **频率**: 约 30 分钟
- **主要任务**: 内存压缩,系统状态检查

### Memory Compactor
- **位置**: `./claw-compactor/scripts/heartbeat_batch.py`
- **触发**: 每次 heartbeat
- **阈值**: savings > 5% 时执行压缩

## 文件存储

### 主存储
- **桌面**: `~/Desktop/` - LinkedIn 数据,业务文件
- **Workspace**: `~/.openclaw/workspace/` - 配置,记忆,技能

### 备份
- **GitHub**: 工作成果同步备份
- **位置**: 待确认具体 repo

## API 配置

### Embedding(待配置)
- **推荐**: SiliconFlow bge-m3(免费)
- **用途**: memorySearch 语义检索

### 其他 API
- (待补充)

*最后更新:2026-03-19 10:20 (Asia/Hong_Kong)*