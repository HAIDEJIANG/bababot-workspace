# Sub-Agent 使用指南

## 📋 快速开始

### 1. 运行 Sub-Agent

```powershell
# 数据合并 Sub-Agent
cd C:\Users\Haide\.openclaw\workspace\projects\subagent-improvement
python agents\subagent_data_merge.py

# 智能优先级打分
python agents\subagent_priority_ranking.py

# 业务意图分析
python agents\subagent_intent_analysis.py

# 线索筛选
python agents\subagent_lead_screening.py
```

### 2. 监控状态

```powershell
# 查看所有 Sub-Agent 状态
python src\subagent_monitor.py list

# 查看运行中的 Sub-Agent
python src\subagent_monitor.py list running

# 查看摘要
python src\subagent_monitor.py summary

# 查看指定 Sub-Agent 状态
python src\subagent_monitor.py status <run_id>

# 查看日志
python src\subagent_monitor.py logs <run_id> 100
```

---

## 🏗️ 架构说明

### 核心组件

**1. Sub-Agent 基类 (`src/subagent_base.py`)**
- 独立工作目录
- 状态管理
- 错误处理
- 日志记录

**2. 资源管理器 (`src/resource_manager.py`)**
- 浏览器锁
- Gmail 锁
- LinkedIn 锁
- StockMarket 锁
- 文件锁

**3. 监控工具 (`src/subagent_monitor.py`)**
- 状态查询
- 日志查看
- 输出文件管理

---

## 🚀 Sub-Agent 详细说明

### 1. 智能优先级打分 Sub-Agent

**目标：** 对 3,185 位联系人进行智能打分，筛选高价值联系人

**打分维度：**

| 维度 | 权重 | 说明 |
|------|------|------|
| **职位相关性** | 100% | CEO/VP/Director/Purchasing/Sales 等 |
| **公司类型** | +20 分 | 航司/MRO/供应商/贸易商 |
| **连接数** | +10 分 | 500+ 连接数加分 |
| **行业匹配** | +5 分 | 航空/航天/发动机/起落架相关 |

**输出文件：**
- `priority_ranking.csv` - 完整优先级排名（3,185 位）
- `high_priority_contacts.csv` - 高优先级联系人（≥80 分）

**筛选标准：**

| 优先级 | 分数 | 职位关键词 | 预估人数 |
|--------|------|----------|---------|
| ⭐⭐⭐ 高 | ≥100 | CEO, COO, CFO, VP, Director | 200-300 |
| ⭐⭐ 中高 | 80-99 | Purchasing, Sales, Business Development | 200-300 |
| ⭐⭐ 中 | 60-79 | Manager, Engineer, Technical | 800-1,200 |
| ⭐ 低 | <60 | Support, Admin, Other | 1,000+ |

### 2. 数据合并 Sub-Agent

**目标：** 合并已有数据和采集数据，解决"Join LinkedIn"问题

**输入：**
- 已有数据：`LINKEDIN Connections_with_posts_FINAL.csv`（3,185 位）
- 采集数据：`contact_profiles_full.csv`（336 位，持续增加）
- 优先级数据：`priority_ranking.csv`（3,185 位）

**输出：**
- `linkedin_master_database.csv` - 完整数据库（3,185 位）
- 100% 姓名/公司/职位完整率
- 解决"Join LinkedIn"问题

### 3. 业务意图分析 Sub-Agent

**目标：** 分析 90 天发帖内容，识别业务意图

**关键词分类：**

| 类型 | 关键词 | 说明 |
|------|------|------|
| **采购意向** | WTB, want to buy, looking for, need, RFQ | 需要购买零件/服务 |
| **出售意向** | WTS, for sale, available, selling, offer | 有零件/服务出售 |
| **合作意向** | partnership, collaboration, distributor | 寻求合作机会 |
| **紧急程度** | urgent, AOG, immediate, ASAP | 紧急需求标记 |

**输出：**
- `linkedin_business_intents.csv` - 业务意图识别结果
- AI 自动分析发帖内容
- 识别采购/出售/合作意向

### 4. 线索筛选 Sub-Agent

**目标：** 基于业务意图和优先级筛选高价值线索

**筛选标准：**
- 业务意图 + 高优先级 = 最高价值
- 紧急需求 = 立即跟进
- 发帖内容匹配 = 高意向

**输出：**
- `linkedin_high_value_leads.csv` - 高价值线索（约 100-300 条）
- `linkedin_recommended_actions.csv` - 推荐跟进动作

---

## 📁 文件结构

```
projects/subagent-improvement/
├── src/
│   ├── subagent_base.py          # Sub-Agent 基类
│   ├── resource_manager.py       # 资源管理器
│   └── subagent_monitor.py       # 监控工具
├── agents/
│   ├── subagent_data_merge.py    # 数据合并 Sub-Agent
│   ├── subagent_priority_ranking.py  # 智能优先级打分 Sub-Agent
│   ├── subagent_intent_analysis.py    # 业务意图分析 Sub-Agent
│   └── subagent_lead_screening.py     # 线索筛选 Sub-Agent
├── scripts/
│   └── linkedin_completion_monitor.py  # LinkedIn 采集完成监控
├── tests/
│   └── test_infrastructure.py    # 基础架构测试
└── USAGE.md                      # 本文档
```

---

## 🔧 创建新的 Sub-Agent

### 模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义 Sub-Agent - 描述
"""

import sys
import pandas as pd
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from subagent_base import SubAgentBase, resource_manager

class MyCustomSubAgent(SubAgentBase):
    """自定义 Sub-Agent"""
    
    def __init__(self):
        super().__init__('my_custom_task')
        # 初始化配置
    
    def execute(self):
        """执行任务"""
        self.log("开始执行...", 'INFO')
        
        # 使用资源锁
        with resource_manager.acquire_browser(self.run_id):
            # 浏览器操作
            pass
        
        # 更新进度
        self.update_progress(50, 100)
        
        # 文件操作（带文件锁）
        with resource_manager.acquire_file('/path/to/file', self.run_id):
            # 文件读写
            pass
        
        # 完成
        self.update_progress(100, 100)
        
        return {'result': 'success'}

if __name__ == '__main__':
    agent = MyCustomSubAgent()
    result = agent.execute_with_retry()
    print(f"完成：{result}")
```

---

## 📊 监控命令详解

### 查看所有 Sub-Agent

```powershell
python src\subagent_monitor.py list
```

输出示例：
```
20260327_073000_data_merge | data_merge | completed | 100/100
20260327_072000_intent_analysis | intent_analysis | running | 50/100
```

### 查看运行中的 Sub-Agent

```powershell
python src\subagent_monitor.py list running
```

### 查看指定 Sub-Agent 状态

```powershell
python src\subagent_monitor.py status 20260327_073000_data_merge
```

输出示例：
```json
{
  "run_id": "20260327_073000_data_merge",
  "task_name": "data_merge",
  "status": "completed",
  "progress": 100,
  "total_items": 100,
  "errors_count": 0,
  "start_time": "2026-03-27T07:30:00",
  "end_time": "2026-03-27T07:35:00",
  "duration_seconds": 300
}
```

### 查看日志

```powershell
python src\subagent_monitor.py logs 20260327_073000_data_merge 100
```

### 查看摘要

```powershell
python src\subagent_monitor.py summary
```

输出示例：
```json
{
  "total": 5,
  "running": 2,
  "completed": 3,
  "failed": 0,
  "total_errors": 0,
  "by_status": {
    "running": 2,
    "completed": 3,
    "failed": 0,
    "initializing": 0
  }
}
```

---

## 🎯 最佳实践

### 1. 独立工作目录

每个 Sub-Agent 有独立的工作目录，避免文件冲突：
```
subagents/
└── run_20260327_073000_data_merge/
    ├── input/
    ├── output/
    ├── logs/
    └── state.json
```

### 2. 资源锁使用

使用资源锁避免冲突：
```python
# 浏览器资源
with resource_manager.acquire_browser(self.run_id):
    # 浏览器操作

# 文件锁
with resource_manager.acquire_file('/path/to/file', self.run_id):
    # 文件读写
```

### 3. 错误重试

自动重试机制：
```python
# 默认重试 3 次
result = agent.execute_with_retry()
```

### 4. 进度更新

及时更新进度：
```python
self.update_progress(current, total)
```

### 5. 日志记录

详细记录日志：
```python
self.log("操作描述", 'INFO')
self.log("错误信息", 'ERROR')
```

---

## 🐛 故障排除

### Sub-Agent 卡住

1. 查看状态：
```powershell
python src\subagent_monitor.py status <run_id>
```

2. 查看日志：
```powershell
python src\subagent_monitor.py logs <run_id> 100
```

3. 检查资源占用：
```python
from src.resource_manager import resource_manager
print(resource_manager.get_usage_report())
```

### 文件锁冲突

确保使用文件锁：
```python
with resource_manager.acquire_file('/path/to/file', self.run_id):
    # 文件操作
```

### 浏览器资源冲突

确保使用浏览器锁：
```python
with resource_manager.acquire_browser(self.run_id):
    # 浏览器操作
```

---

## 📞 支持

**文档：**
- `README.md` - 项目说明
- `USAGE.md` - 使用指南（本文档）
- `src/subagent_base.py` - 基类文档
- `src/resource_manager.py` - 资源管理器文档

**日志位置：**
- Sub-Agent 日志：`C:\Users\Haide\.openclaw\workspace\subagents\run_<timestamp>_<task>\logs\`

**输出位置：**
- 数据文件：`C:\Users\Haide\Desktop\LINKEDIN\`

---

**最后更新：** 2026-03-27 10:05
