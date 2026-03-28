# LinkedIn 数据整合方案

## 📋 方案概述

**目标：** 合并已有数据和自动采集数据，生成完整数据库

**输入数据源：**
1. 已有文件：`LINKEDIN Connections_with_posts_FINAL.csv`（3,185 位，完整姓名/公司/职位）
2. 自动采集：`contact_profiles_full.csv`（采集中，含 90 天发帖）
3. 优先级打分：`priority_ranking.csv`（3,185 位，已打分）

**输出文件：**
- `linkedin_master_database.csv`（完整数据库）
- `linkedin_business_leads.csv`（高意向线索）

---

## 🔄 整合流程

### Phase 1: 数据准备（等待采集完成）

**等待条件：**
- ✅ 自动采集完成（contact_profiles_full.csv）
- ✅ 90 天发帖数据完整（contact_posts_90days.csv）

**预计时间：** 约 25-28 小时（明晚完成）

---

### Phase 2: 数据合并（1-2 小时）

**步骤 1: 读取所有数据源**

```python
# 读取已有数据（完整姓名/公司/职位）
existing_data = pd.read_csv('LINKEDIN Connections_with_posts_FINAL.csv')

# 读取自动采集数据（含发帖）
collected_data = pd.read_csv('contact_profiles_full.csv')
posts_data = pd.read_csv('contact_posts_90days.csv')

# 读取优先级打分
priority_data = pd.read_csv('priority_ranking.csv')
```

**步骤 2: 按 URL/Profile ID 匹配合并**

```python
# 以 URL 为键合并
merged = pd.merge(
    existing_data,
    collected_data,
    on='URL',
    how='left',
    suffixes=('_existing', '_collected')
)

# 优先使用已有数据的姓名/公司/职位（解决"Join LinkedIn"问题）
merged['name'] = merged['First Name'] + ' ' + merged['Last Name']
merged['company'] = merged['Company'].fillna(merged['current_company'])
merged['position'] = merged['Position'].fillna(merged['current_title'])
```

**步骤 3: 整合优先级打分**

```python
# 合并优先级分数
final = pd.merge(
    merged,
    priority_data,
    left_on='URL',
    right_on='contact_id',
    how='left'
)
```

**步骤 4: 保存完整数据库**

```python
# 输出完整数据库
final.to_csv('linkedin_master_database.csv', index=False, encoding='utf-8-sig')
```

---

### Phase 3: 业务意图识别（2-4 小时）

**步骤 1: 分析发帖内容**

```python
# 业务意图关键词
BUY_KEYWORDS = ['WTB', 'looking for', 'need', 'RFQ', 'quote', 'buy']
SELL_KEYWORDS = ['WTS', 'for sale', 'available', 'selling', 'offer']
PARTNERSHIP_KEYWORDS = ['partnership', 'collaboration', 'distributor']

def analyze_intent(post_content):
    content = str(post_content).lower()
    if any(kw in content for kw in BUY_KEYWORDS):
        return '采购意向'
    elif any(kw in content for kw in SELL_KEYWORDS):
        return '出售意向'
    elif any(kw in content for kw in PARTNERSHIP_KEYWORDS):
        return '合作意向'
    else:
        return '一般动态'
```

**步骤 2: 生成高意向线索**

```python
# 筛选高意向联系人
high_intent = final[final['business_intent'].isin(['采购意向', '出售意向', '合作意向'])]

# 按优先级排序
high_intent = high_intent.sort_values('total_score', ascending=False)

# 保存高意向线索
high_intent.to_csv('linkedin_business_leads.csv', index=False, encoding='utf-8-sig')
```

---

## 📊 输出文件结构

### 1. linkedin_master_database.csv（完整数据库）

| 字段 | 来源 | 说明 |
|------|------|------|
| contact_id | 采集 | 联系人 ID |
| name | 已有 | 姓名（优先使用已有数据） |
| company | 已有 | 公司（优先使用已有数据） |
| position | 已有 | 职位（优先使用已有数据） |
| email | 已有 | 邮箱 |
| connected_on | 已有 | 连接日期 |
| current_title | 采集 | 采集的职位（备用） |
| current_company | 采集 | 采集的公司（备用） |
| location | 采集 | 所在地 |
| connections | 采集 | 连接数 |
| post_count_90d | 采集 | 90 天发帖数 |
| total_score | 打分 | 优先级总分 |
| priority_level | 打分 | 优先级等级 |

**数据量：** 3,185 位联系人

---

### 2. linkedin_business_leads.csv（高意向线索）

| 字段 | 说明 |
|------|------|
| contact_id | 联系人 ID |
| name | 姓名 |
| company | 公司 |
| position | 职位 |
| post_date | 发帖日期 |
| post_content | 发帖内容 |
| business_intent | 业务意图（采购/出售/合作） |
| priority_score | 优先级分数 |
| recommended_action | 推荐跟进动作 |

**预计数据量：** 100-300 条高价值线索

---

## ⏱️ 时间规划

| 阶段 | 任务 | 预计时间 |
|------|------|---------|
| **Phase 1** | 等待采集完成 | ~25-28 小时 |
| **Phase 2** | 数据合并 | 1-2 小时 |
| **Phase 3** | 业务意图识别 | 2-4 小时 |
| **总计** | - | **约 30-34 小时** |

---

## 🛠️ 技术实现

### 脚本文件：`linkedin_data_merge.py`

**功能：**
1. 读取所有数据源
2. 按 URL 匹配合并
3. 解决"Join LinkedIn"问题
4. 整合优先级打分
5. 业务意图识别
6. 输出完整数据库和高意向线索

**依赖：**
```
pandas
openpyxl
xlrd
```

---

## ✅ 质量保证

### 数据完整性检查

**检查项：**
- ✅ 姓名完整率：100%（来自已有数据）
- ✅ 公司完整率：100%（来自已有数据）
- ✅ 职位完整率：100%（来自已有数据）
- ✅ 发帖数据：尽可能完整（取决于采集）
- ✅ 优先级打分：100%（已完成）

### 数据一致性检查

**检查项：**
- ✅ URL 唯一性：无重复
- ✅ 联系人 ID 匹配：100%
- ✅ 优先级分数范围：0-120 分

---

## 📋 后续使用

### 1. 高优先级联系人跟进

**筛选条件：**
```python
# 高优先级 + 高意向
high_priority_leads = final[
    (final['total_score'] >= 80) & 
    (final['business_intent'].isin(['采购意向', '出售意向', '合作意向']))
]
```

### 2. 定制化联系策略

**按优先级分类：**
- ⭐⭐⭐ 高优先级（80-120 分）：立即联系，定制话术
- ⭐⭐ 中优先级（60-79 分）：定期跟进，观察动态
- ⭐ 低优先级（0-59 分）：保持关注，按需联系

### 3. 定期更新

**更新频率：**
- 发帖数据：每周更新一次
- 优先级打分：每月重新评估
- 业务意图：实时监测新发帖

---

## 🚨 风险与应对

### 风险 1: 采集未完成

**应对：**
- ✅ 断点续传功能已启用
- ✅ 可随时中断后继续
- ✅ 进度自动保存

### 风险 2: 数据匹配失败

**应对：**
- ✅ 使用 URL 作为主键（最可靠）
- ✅ 备用匹配：姓名 + 公司组合
- ✅ 人工审核不匹配记录

### 风险 3: "Join LinkedIn"问题

**应对：**
- ✅ 优先使用已有数据的姓名/公司/职位
- ✅ 采集数据作为补充和验证
- ✅ 发帖数据不受影响

---

## 📞 需要确认的事项

**待老板决策：**

1. **数据整合时机**
   - [ ] 等待采集完成后统一整合（推荐）
   - [ ] 先整合已采集部分（约 13%）
   - [ ] 分批次整合（每 25% 一次）

2. **业务意图识别范围**
   - [ ] 全部 3,185 位联系人
   - [ ] 仅高优先级（2,770 位）
   - [ ] 仅已采集部分

3. **输出文件格式**
   - [ ] CSV（推荐，兼容性好）
   - [ ] Excel（.xlsx，便于查看）
   - [ ] 两者都输出

---

**方案制定时间：** 2026-03-26 21:58
**预计执行时间：** 采集完成后（约 2026-03-27 晚间）

---

**老板，数据整合方案已准备完成！请审阅并指示是否需要调整。** ✈️
