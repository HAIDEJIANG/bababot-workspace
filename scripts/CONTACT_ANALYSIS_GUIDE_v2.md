# LinkedIn 联系人深度分析系统 v2.0 - 动态增量版

## 📋 系统概述

**目标**: 全部 LinkedIn 联系人动态分析（支持新增/更新/全量三种模式）

**节奏**: 10-15 人/小时（间隔 240-360 秒随机）

**预计完成**: 约 9-13 天（按 3000 人计算）

**核心特性**:
- ✅ 24 小时不间断运行（无夜间静默）
- ✅ 每条数据即时保存（防止丢失）
- ✅ 断点续传（中断后可恢复）
- ✅ 异常自动熔断 + 恢复
- ✅ 保留原有分析结果（新建输出目录）
- ✅ **动态联系人列表**（支持增减变化）
- ✅ **增量分析模式**（新增自动加入）
- ✅ **定期更新模式**（90 天自动刷新）

---

## 🗂️ 文件结构

### 输入文件（需准备）
```
C:\Users\Haide\Desktop\LINKEDIN\
├── all_contacts_current.csv    # 当前全部联系人（从 LinkedIn 导出）
├── analyzed_history.csv        # 已分析历史记录（自动创建）
└── analysis_queue.csv          # 待分析队列（自动创建）
```

### 输出文件（自动生成）
```
C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\
├── contact_profiles_full.csv   # Profile 数据总表
├── contact_posts_90days.csv    # 90 天发帖记录
├── business_leads.csv          # 高意向线索
├── analysis_summary.json       # 本次分析汇总
├── delta_report.md             # 增量报告
├── progress.json               # 进度追踪（断点续传）
├── analysis_log_*.txt          # 运行日志
└── backups/                    # 定期备份
    └── progress_backup_*.json
```

---

## 🚀 快速启动

### 步骤 1: 导出 LinkedIn 联系人

**方法 A: LinkedIn 官方导出**
1. 访问：https://www.linkedin.com/psettings/member-data
2. 选择"想要什么数据" → 勾选"连接"
3. 选择语言 → 请求存档
4. 等待邮件通知（约 10 分钟）
5. 下载 CSV 并复制到：`C:\Users\Haide\Desktop\LINKEDIN\all_contacts_current.csv`

**方法 B: 使用现有分析结果**
如果已有联系人列表，确保包含以下字段：
- `contact_id` 或 `id`（唯一标识）
- `name`（姓名）
- `profile_url` 或 `linkedin_url`（LinkedIn 主页链接）
- `company`（公司，可选）
- `title`（职位，可选）

### 步骤 2: 启动 WebTop 持久化浏览器

```powershell
cd C:\Users\Haide\.openclaw\workspace\scripts
python webtop/webtop_local.py --start
```

在打开的浏览器中手动登录 LinkedIn。

### 步骤 3: 选择分析模式

编辑脚本 `contact_deep_analysis_v1.py` 第 57 行：

```python
ANALYSIS_MODE = 'incremental'  # 可选：'full' / 'incremental' / 'update'
```

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **full** | 分析全部联系人 | 首次运行 |
| **incremental** | 仅分析新增联系人 | 日常运行（推荐） |
| **update** | 重新分析超过 90 天未更新的 | 定期刷新动态 |

### 步骤 4: 启动分析

```powershell
cd C:\Users\Haide\.openclaw\workspace\scripts
python contact_deep_analysis_v1.py
```

### 步骤 5: 中断后恢复

直接重新运行即可，自动从断点续传：

```powershell
python contact_deep_analysis_v1.py
```

---

## 📊 输出说明

### 1. contact_profiles_full.csv

| 字段 | 说明 |
|------|------|
| contact_id | 联系人 ID |
| name | 姓名 |
| current_company | 当前公司 |
| current_title | 当前职位 |
| location | 所在地 |
| industry | 行业 |
| connections | 连接数 |
| about | 个人简介 |
| experience | 工作经历 |
| education | 教育背景 |
| skills | 技能 |
| crawl_time | 抓取时间 |
| profile_url | LinkedIn 主页链接 |

### 2. contact_posts_90days.csv

| 字段 | 说明 |
|------|------|
| contact_id | 联系人 ID |
| contact_name | 联系人姓名 |
| post_date | 发帖日期 |
| post_content | 发帖内容（前 5000 字） |
| post_url | 帖子链接 |
| has_business_intent | 是否业务相关（Yes/No） |
| matched_keywords | 匹配的业务关键词 |
| crawl_time | 抓取时间 |

### 3. business_leads.csv（高意向线索）

| 字段 | 说明 |
|------|------|
| contact_id | 联系人 ID |
| contact_name | 联系人姓名 |
| company | 公司 |
| title | 职位 |
| business_intent | 业务意图（Yes/No） |
| matched_keywords | 匹配关键词 |
| last_post_date | 最近发帖日期 |
| priority_score | 优先级打分（0-100） |
| recommended_action | 推荐跟进动作 |
| crawl_time | 抓取时间 |

**优先级打分规则**:
- 业务相关发帖数量（40%）
- 职位匹配度（30%）
- 最近活跃度（20%）
- 连接数（10%）

**推荐动作**:
- ≥80 分：立即联系 - 高优先级
- ≥60 分：本周内联系 - 中优先级
- ≥40 分：本月内联系 - 低优先级
- <40 分：保持关注 - 暂不联系

### 4. analysis_summary.json

本次分析的汇总统计（JSON 格式）：
```json
{
  "analysis_mode": "incremental",
  "total_contacts": 3185,
  "processed_contacts": 50,
  "new_contacts_count": 30,
  "updated_contacts_count": 20,
  "success_rate": 98.5,
  ...
}
```

### 5. delta_report.md

增量报告（Markdown 格式），包含：
- 分析模式
- 分析时间范围
- 新增联系人数量
- 更新联系人数量
- 成功率统计

---

## 🛡️ 安全策略

### 1. 节奏控制
- 每人间隔：240-360 秒（4-6 分钟随机）
- 目标速度：10-15 人/小时
- 单账号上限：**不设限额**（根据实际执行情况调整）

### 2. 异常熔断
- 连续失败 5 次 → 暂停 30 分钟
- 30 分钟内无失败 → 重置计数器
- 熔断触发 → 自动记录日志

### 3. 数据保护
- 每条数据即时保存（flush 到磁盘）
- 每 10 人自动备份进度
- 断点续传（中断后直接重跑）

### 4. 账号保护
- 25 个账号池轮换（通过 Cookie 管理）
- 模拟真人行为（随机滚动/停留）
- Stealth 反检测（Playwright 插件）

---

## 🔄 日常运维流程

### 每日检查（建议固定时间）

```powershell
# 1. 查看最新日志
Get-Content C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\analysis_log_*.txt -Tail 50

# 2. 查看进度
Get-Content C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\progress.json

# 3. 查看汇总报告
Get-Content C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\analysis_summary.json
```

### 每周维护

1. **更新联系人列表**（如有新增）
   - 重新从 LinkedIn 导出
   - 替换 `all_contacts_current.csv`
   - 运行增量模式：`ANALYSIS_MODE = 'incremental'`

2. **检查账号健康**
   - 查看日志中的失败率
   - 如失败率 > 10%，降低频率或切换账号

3. **备份输出数据**
   ```powershell
   # 复制到备份目录
   Copy-Item C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\*.* -Destination D:\Backup\LinkedIn\
   ```

### 每月更新

运行一次全量更新模式：
```python
ANALYSIS_MODE = 'update'  # 重新分析超过 90 天的联系人
```

---

## ⚠️ 故障处理

### 问题 1: 浏览器未运行
**错误**: `启动浏览器失败：连接被拒绝`

**解决**:
```powershell
# 启动 WebTop 浏览器
python webtop/webtop_local.py --start

# 等待 10 秒后重新运行
```

### 问题 2: LinkedIn 登录过期
**错误**: Profile 页面无法访问

**解决**:
1. 在打开的浏览器中手动重新登录 LinkedIn
2. 重新运行分析脚本（自动续传）

### 问题 3: 连续失败触发熔断
**日志**: `触发熔断：连续失败 5 次，暂停 30 分钟`

**解决**:
- 等待 30 分钟自动恢复
- 或手动检查网络连接、浏览器状态
- 检查 LinkedIn 是否可手动访问

### 问题 4: 输入文件不存在
**日志**: `全部联系人文件不存在：all_contacts_current.csv`

**解决**:
1. 从 LinkedIn 导出联系人数据
2. 或创建空文件（至少包含表头）
3. 或切换为全量模式：`ANALYSIS_MODE = 'full'`

---

## 📈 预期成果

### 完成时间（预估）
| 联系人数 | 速度（人/小时） | 预计时间 |
|---------|----------------|---------|
| 1,000 | 12 | ~83 小时 ≈ 3.5 天 |
| 3,000 | 12 | ~250 小时 ≈ 10.4 天 |
| 5,000 | 12 | ~417 小时 ≈ 17.4 天 |

### 输出数据量（预估）
- **Profile 数据**: 与联系人数一致
- **发帖记录**: 约 50,000-100,000 条（按每人 15-30 条估算）
- **高意向线索**: 约 500-1,000 条（按 15-30% 转化率估算）

### 业务价值
1. **完整人脉画像**: 全部联系人的详细背景
2. **业务意图识别**: 自动筛选高意向潜在客户
3. **优先级排序**: 推荐跟进顺序，提高效率
4. **持续监控**: 可定期重跑，追踪动态变化

---

## 🔧 配置参数

在脚本顶部修改以下参数：

```python
# 分析模式
ANALYSIS_MODE = 'incremental'  # 'full' / 'incremental' / 'update'
REFRESH_ANALYZED_DAYS = 90     # 已分析联系人超过 90 天则重新分析

# 执行节奏
MIN_INTERVAL_SECONDS = 240  # 最小间隔 4 分钟
MAX_INTERVAL_SECONDS = 360  # 最大间隔 6 分钟
TARGET_PER_HOUR = 12  # 目标每小时 12 人

# 安全配置
MAX_CONSECUTIVE_FAILURES = 5  # 连续失败 5 次熔断
MAX_PROFILE_SCROLLS = 5  # 每人最多滚动 5 次
MAX_POSTS_PER_CONTACT = 100  # 每人最多抓取 100 条发帖
```

---

## 📞 支持

**日志位置**: `C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\analysis_log_*.txt`

**进度文件**: `C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\progress.json`

**备份目录**: `C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\backups\`

**汇总报告**: `C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\analysis_summary.json`

**增量报告**: `C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\delta_report.md`

---

## 📝 版本历史

- **v2.0 (2026-03-26)**: 动态增量版
  - ✅ 支持动态联系人列表（增减变化）
  - ✅ 增量分析模式（仅分析新增）
  - ✅ 更新模式（90 天自动刷新）
  - ✅ 已分析历史记录追踪
  - ✅ 增量报告生成

- **v1.0 (2026-03-26)**: 基础版
  - ✅ 24 小时不间断运行
  - ✅ 即时保存 + 断点续传
  - ✅ 异常熔断保护

---

**最后更新**: 2026-03-26 12:55 GMT+8

**状态**: ✅ 就绪，等待启动

**下一步**: 准备联系人 CSV 文件 → 启动浏览器 → 运行分析
