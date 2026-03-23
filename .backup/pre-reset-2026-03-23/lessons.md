# 教训记录 (Lessons Learned)
**更新时间**: 2026-03-19
**用途**: 踩过的坑,按严重程度分级
**分级**: CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW

---

## CRITICAL - 严重教训

### [2026-03-05] 数据真实性原则
- **问题**: 因 LinkdAPI 限制,在 LinkedIn 帖子总表中添加了 10 条示例数据
- **影响**: 违反用户"只保留真实数据"的核心原则
- **教训**: 即使 API 受限,也不能用示例数据填充,必须寻找其他真实数据采集方法或明确报告问题
- **用户反馈**: "绝对禁止在 LinkedIn 帖子信息总表中输入任何示例数据,推测数据,模拟数据"
- **标签**: #data-integrity #linkedin #critical

### [2026-03-15] RFQ Condition 筛选规则
- **问题**: 用户多次提醒后仍未立即执行 DIST 跳过规则
- **影响**: 向 DIST 供应商发送了不应发送的 RFQ
- **教训**: 用户重复强调的指令必须立即执行并记录,不能反复确认
- **用户反馈**: "我说了好多好多次了,把这个写进你那该死的记忆里!"
- **规则**: Condition 为 DIST 的供应商,直接跳过,不发送 RFQ
- **标签**: #rfq #aviation #user-instructions

## 🟠 HIGH - 重要教训

### Browser Relay 稳定性
- **问题**: Browser Relay 偶尔断开,影响 LinkedIn 数据采集
- **当前方案**: watchdog 机制监控
- **待改进**: 更稳定的自动重连机制
- **标签**: #browser #infrastructure #stability

## 🟡 MEDIUM - 中等教训
(暂无)

## 教训使用指南

### 检索方式
使用 `memory_search` 查询特定主题的教训:
```
memory_search(query="RFQ Condition 规则")

### 添加新教训
当遇到新问题时,立即记录到 `memory/<today>.md`,然后定期整理到此文件.

*最后更新:2026-03-19 10:20 (Asia/Hong_Kong)*