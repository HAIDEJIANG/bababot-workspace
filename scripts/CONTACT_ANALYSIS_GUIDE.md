# LinkedIn 联系人深度分析系统 v1.0

## 📋 系统概述

**目标**: 3,185 位 LinkedIn 联系人全部深度分析（Profile + 90 天发帖）

**节奏**: 10-15 人/小时（间隔 240-360 秒随机）

**预计完成**: 9-13 天（24 小时不间断）

**核心特性**:
- ✅ 24 小时不间断运行（无夜间静默）
- ✅ 每条数据即时保存（防止丢失）
- ✅ 断点续传（中断后可恢复）
- ✅ 异常自动熔断 + 恢复
- ✅ 保留原有分析结果（新建输出目录）

---

## 📁 文件结构

```
C:\Users\Haide\Desktop\LINKEDIN\
├── high_priority_contacts.csv          # 输入：高优先级联系人
├── ANALYSIS_20260326/                  # 输出目录（按日期）
│   ├── contact_profiles_full.csv       # Profile 数据总表
│   ├── contact_posts_90days.csv        # 90 天发帖记录
│   ├── business_leads.csv              # 高意向线索
│   ├── progress.json                   # 进度追踪（断点续传）
│   ├── analysis_log_*.txt              # 运行日志
│   └── backups/                        # 定期备份
│       └── progress_backup_*.json
```

---

## 🚀 快速启动

### 前置条件

1. **WebTop 持久化浏览器已运行**
```powershell
python scripts/webtop/webtop_local.py --start
```

2. **LinkedIn 已登录**（在打开的浏览器中）

3. **输入文件就绪**
```
C:\Users\Haide\Desktop\LINKEDIN\high_priority_contacts.csv
```

### 启动分析

```powershell
cd C:\Users\Haide\.openclaw\workspace\scripts
python contact_deep_analysis_v1.py
```

### 中断后恢复

```powershell
# 直接重新运行即可，会自动从断点续传
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

## 🔧 配置参数

在脚本顶部修改以下参数：

```python
# 执行节奏
MIN_INTERVAL_SECONDS = 240  # 最小间隔 4 分钟
MAX_INTERVAL_SECONDS = 360  # 最大间隔 6 分钟
TARGET_PER_HOUR = 12  # 目标每小时 12 人

# 安全配置
MAX_CONSECUTIVE_FAILURES = 5  # 连续失败 5 次熔断
MAX_PROFILE_SCROLLS = 5  # 每人最多滚动 5 次
MAX_POSTS_PER_CONTACT = 100  # 每人最多抓取 100 条发帖

# 关键词配置
BUSINESS_KEYWORDS = [...]  # 业务意图关键词
EXCLUDE_KEYWORDS = [...]   # 排除关键词
```

---

## 📈 进度监控

### 实时日志
```powershell
# 查看最新日志
Get-Content C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\analysis_log_*.txt -Tail 50 -Wait
```

### 进度查询
```powershell
# 查看进度文件
Get-Content C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\progress.json
```

### 统计信息
日志中每小时自动输出：
- 已处理人数
- 失败人数
- 当前速度（人/小时）
- 预计完成时间

---

## 🎯 关键词策略

### 业务意图关键词（保留）
```
WTB, WTS, WTP, want to buy, want to sell
RFQ, request for quote, for sale, available
stock, inventory, looking for, need
offer, quote, price, USD, $
WhatsApp, email me, contact me, DM me
urgent, AOG, immediate
PN#, Part Number, S/N, serial
CFM56, V2500, PW4000, LEAP, Trent
A320, B737, B777, A350, APU
Landing Gear, Engine, Spare parts, Aviation
```

### 排除关键词（非业务）
```
hiring, recruiting, we are hiring
conference, event, webinar, summit
award, promotion, proud to announce
article, blog, read more
```

---

## ⚠️ 故障处理

### 问题 1: 浏览器未运行
**错误**: `启动浏览器失败：连接被拒绝`

**解决**:
```powershell
# 启动 WebTop 浏览器
python scripts/webtop/webtop_local.py --start

# 等待 10 秒后重新运行分析脚本
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

### 问题 4: 数据抓取不完整
**原因**: 页面加载慢或滚动不足

**解决**:
```python
# 修改配置增加滚动次数
MAX_PROFILE_SCROLLS = 10  # 从 5 增加到 10
```

---

## 📊 预期成果

### 完成时间
- **总人数**: 3,185 人
- **速度**: 10-15 人/小时
- **预计**: 212-318 小时 ≈ **9-13 天**

### 输出数据量（预估）
- **Profile 数据**: 3,185 条
- **发帖记录**: 约 50,000-100,000 条（按每人 15-30 条估算）
- **高意向线索**: 约 500-1,000 条（按 15-30% 转化率估算）

### 业务价值
1. **完整人脉画像**: 3,185 位联系人的详细背景
2. **业务意图识别**: 自动筛选高意向潜在客户
3. **优先级排序**: 推荐跟进顺序，提高效率
4. **持续监控**: 可定期重跑，追踪动态变化

---

## 🔄 后续优化

### Phase 1: 基础版（当前）
- ✅ Profile 数据抓取
- ✅ 90 天发帖抓取
- ✅ 业务意图识别
- ✅ 优先级打分

### Phase 2: 增强版（后续）
- [ ] 公司官网信息补充（Scrapy）
- [ ] 邮箱/电话验证
- [ ] 互动记录追踪（CRM）
- [ ] 自动跟进提醒

### Phase 3: 智能化（后续）
- [ ] AI 分析发帖情感倾向
- [ ] 智能推荐联系话术
- [ ] 业务匹配度深度学习
- [ ] 转化效果追踪优化

---

## 📞 支持

**日志位置**: `C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\analysis_log_*.txt`

**进度文件**: `C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\progress.json`

**备份目录**: `C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\backups\`

---

**最后更新**: 2026-03-26 12:46 GMT+8

**版本**: v1.0

**状态**: ✅ 就绪，等待启动
