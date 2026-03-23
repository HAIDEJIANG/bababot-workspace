# 重要脚本工作记录 - 2026-03-20

## 核心原则
**脚本是重要的工作内容,必须保存在深层记忆中**

---

## 已创建的重要脚本

### 1. RFQ 自动询价脚本系列

#### runner_v3_stable.py(v3.0 稳定性增强版)
- **位置**: `scripts/rfq_auto/runner_v3_stable.py`, **大小**: 12.4KB, **创建时间**: 2026-03-20 18:43, **核心功能**:, 浏览器会话管理 - 自动检测/恢复连接
 - 多重元素定位策略 - 3 层选择器回退机制
 - 智能等待逻辑 - 动态检测页面加载完成
 - 错误恢复机制 - 自动重试 + 断点续传
 - 进度持久化 - 每项完成后立即保存
 - 速率限制 - 避免过快触发反爬虫

 - **成功记录**:
 - RFQ20260318-01 四川海特 42 项(100% 完成)
 - 实际运行时间:15 分 22 秒(最终批次)
 - 提交总数:100+ 次 RFQ
 - 成功率:100%

#### 其他 RFQ 脚本
- `rfq_auto_submit_final.py` - 13.5KB, `rfq_complete_auto.py` - 20.4KB, `rfq_submit_3pn.py` - 19.1KB, `rfq_playwright_auto.py` - 13.3KB

### 2. LinkedIn 采集脚本系列

#### linkedin_collection_v2.py(v2.0 带 New Posts 刷新)
- **位置**: `scripts/linkedin_collection_v2.py`, **大小**: 6.5KB, **创建时间**: 2026-03-20 21:19
 - 重复度检测机制 - 超过 70% 重复自动刷新
 - New Posts 自动刷新 - 获取新鲜内容
 - 持续深度采集 - 确保采集时间达标(≥60 分钟)
 - 进度追踪 - 实时记录采集状态

- **配置参数**:
 ```python
 TARGET_DURATION_MINUTES = 60 # 目标采集时长
 SCROLL_PAUSE_SECONDS = 3 # 滚动等待时间
 MAX_SCROLLS_PER_CYCLE = 10 # 每轮最大滚动次数
 DUPLICATE_THRESHOLD = 0.7 # 重复率阈值 70%
 ```

 - 多次 LinkedIn 采集任务, 累计新增 11+ 条高价值业务数据, 数据质量:100% 真实数据,source_url 可追溯

#### 其他 LinkedIn 脚本
- `linkedin_business_collector.py` - 11.3KB, `collect_linkedin_batch10.py` - 13.0KB, `append_linkedin_batch_*.py` - 多个批次追加脚本

### 3. 邮件处理脚本

#### imap-smtp-email 系列
 - **位置**: `skills/imap-smtp-email/scripts/`
 - **核心脚本**:
 - `imap.js` - IMAP 邮件收取
 - `smtp.js` - SMTP 邮件发送
 - `config.js` - 配置管理

- **配置信息**:
 sale@aeroedgeglobal.com
 IMAP: imaphz.qiye.163.com:993 (SSL)
 授权码:A4D8%b3x6FHAH45d

 jianghaide@aeroedgeglobal.com
 授权码:arv9KztNY$JWaHx3

 - DOMAS 邮件搜索和整理
 - Blue Sky Technics 邮件解析
 - 自动提取器材需求到 Excel

### 4. 系统工具脚本

#### heartbeat_optimized.py
- **位置**: `scripts/heartbeat_optimized.py`
- **功能**: 统一心跳检查(内存压缩 + 系统状态 + Evolver 安全检查)

#### system_status_check.py
- **位置**: `scripts/system_status_check.py`
- **功能**: Git 状态 + 子 Agent 状态 + 系统健康检查

#### git_status_layered.py
- **位置**: `scripts/git_status_layered.py`
- **功能**: 分层 Git 状态报告

## 脚本开发经验教训

### 成功实践
1. **版本迭代**
 - v1.0 → v2.0 → v3.0 持续优化
 - 每个版本解决前版本的问题

2. **错误处理**
 - 自动重试机制(最多 3 次), 断点续传功能, 进度持久化(每项完成后保存)

3. **稳定性增强**
 - 浏览器会话管理, 多重元素定位策略, 智能等待逻辑

4. **质量保障**
 - 数据验证(100% 真实数据), source_url 可追溯, 无模拟数据

### ️ 重要教训
1. **时间报告**
 - 禁止估算时间("预计 50-70 分钟")
 - 只报告实际运行时间

2. **用户干预**
 - 避免中途请求确认
 - 全自动执行,完成后汇报

3. **浏览器稳定性**
 - 使用 browser 工具直接操作, 自动检测/恢复会话连接, 遇到超时自动重启

4. **速率限制处理**
 - clawhub 安装遇到速率限制时, 使用替代方案(GitHub 克隆,手动下载), 或等待 5-10 分钟后重试

## 脚本文件管理

### 目录结构
C:/Users/Haide/.openclaw/workspace/
├── scripts/
│ ├── rfq_auto/
│ │ ├── runner_v3_stable.py
│ │ ├── runner_v2.py
│ │ ├── outputs/
│ │ └── ...
│ ├── linkedin_collection_v2.py
│ ├── heartbeat_optimized.py
│ └── ...
├── skills/
│ └── imap-smtp-email/
│ └── scripts/
│ ├── imap.js
│ ├── smtp.js
│ └── config.js
└── memory/
 └── skills/
 ├── proactive-agent.md
 ├── clawfeed.md
 └── installation-methods.md

### 备份策略
- GitHub 版本控制, 本地备份:`C:/Users/Haide/Desktop/OPENCLAW/`, 定期导出重要脚本

## 脚本使用场景

### RFQ 自动询价
- 场景:航材供应商询价, 脚本:`runner_v3_stable.py`, 规则:Condition 过滤(NE>FN>NS>OH>SV>AR)
- 输出:Excel 进度表 + JSON 结果

### LinkedIn 信息采集
- 场景:航空业务信息收集
- 脚本:`linkedin_collection_v2.py`
- 规则:≥60 分钟实际运行,New Posts 刷新
- 输出:CSV 数据 + Markdown 报告

### 邮件处理
- 场景:供应商邮件搜索和整理, 脚本:`imap.js` + 自定义提取脚本, 规则:自动提取器材需求, 输出:Excel 汇总表

## 未来脚本开发计划
1. **RFQ 优化**
 - 支持更多供应商平台, 智能报价分析, 自动回复供应商

2. **LinkedIn 增强**
 - 支持群组采集, 智能内容分类, 自动打标签

3. **邮件自动化**
 - 自动分类和归档, 智能回复生成, 报价自动提取

4. **监控和预警**
 - proactive-agent 集成, 异常自动报警, 定时任务调度

*记录时间:2026-03-20 21:21*
*这是核心工作内容,必须永久保存在深层记忆中!*