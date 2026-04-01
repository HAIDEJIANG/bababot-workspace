# USER.md - About Your Human

**Name**: HAIDEJIANG (王海江)
**What to call them**: 老板 / 您
**Pronouns**: 他/他
**Timezone**: Asia/Hong_Kong (Asia/Shanghai)

## Context

### 核心业务
航空行业专业从业者，主要业务领域：
- 航材交易（采购/销售）
- 飞机发动机（CFM56、V2500、PW 系列等）
- 起落架（租赁/维修/交易）
- 飞机整机（买卖/租赁/维修）
- MRO 服务（维修、保养、大修）

### 关键项目
1. **LinkedIn 联系人分析系统**
   - 总联系人：3,185 位
   - 已分析：~500 位 (16% 完成)
   - 文件位置：`~/Desktop/LINKEDIN/`
   - 状态：持续分析中

2. **LinkedIn 业务信息采集系统**
   - 基于 bababot 方法（实际数据优先）
   - 只保留真实 LinkedIn 帖子数据
   - 总表：`~/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv`
   - 当前真实数据：998 条有效记录（覆盖 362 家公司/发布者，328 条有联系方式）
   - 状态：Cron 定时运行中（每 4 小时增量采集）

3. **RFQ Inquiry Trial (进行中)**
   - 项目时间：2025-07-09 启动
   - 任务状态：已进入自动提交流程（按有效 Condition 筛选并以"RFQ SENT/成功回执"为准）
   - 最新进展（2026-03-25）:
     * 总 PN 数：53 个
     * 已完成：42 个 (100%)
     * RFQ 发送总数：99 条
     * 待执行：PN 44-53 (10 个，根据新 Excel 添加)
   - 效率对比：自动化脚本比浏览器手动快 624 倍（936 条/小时 vs 1.5 条/小时）
   - 文件位置：`rfq_inquiry_progress.md`

4. **自动化工作流程**
   - WORKFLOW_AUTO.md 定义标准流程
   - 心跳检查定期维护系统健康
   - GitHub 同步保存所有工作成果
   - Browser Relay 监控：自动检测断开/恢复（当前以 watchdog 机制为主）

### 重要偏好
- **数据真实性至上**：只保留真实 LinkedIn 帖子，删除所有模拟数据
- **业务导向**：所有分析围绕航材、发动机、起落架、飞机整机业务展开
- **效率优先**：快速响应，直接给出 actionable insights
- **文件管理**：桌面文件夹为主存储，GitHub 为备份
- **表格软件偏好**：默认使用 WPS 打开所有表格文件

### 技术栈
- OpenClaw + Browser Relay 进行 LinkedIn 数据采集
- Python 脚本进行批量分析和数据处理
- Excel/CSV 进行数据管理和汇总
- GitHub 进行版本控制和备份

### 当前关注点
1. 修复 Browser Relay 稳定性问题，获取更多真实 LinkedIn 数据
2. 验证专业推断分析的准确性
3. 将分析结果转化为实际业务联系
4. 建立更稳定的技术基础设施

### 沟通习惯
- 直接下达任务指令
- 重视结果而非过程描述
- 对航空行业专业术语熟悉
- 偏好中文交流

---
_Last updated: 2026-04-01_
