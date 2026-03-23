# USER.md - About Your Human

**Name**: HAIDEJIANG (王海江)
**What to call them**: 老板 / 您
**Pronouns**: 他/他
**Timezone**: Asia/Hong_Kong (Asia/Shanghai)

## Context

### 核心业务
航空行业专业从业者，主要业务领域：
- 航材交易（采购/销售）
- 飞机发动机（CFM56、V2500、PW系列等）
- 起落架（租赁/维修/交易）
- 飞机整机（买卖/租赁/维修）
- MRO服务（维修、保养、大修）

### 关键项目
1. **LinkedIn联系人分析系统**
   - 总联系人：3,185位
   - 已分析：1,529位 (48%完成)
   - 高优先级：1,061位可直接联系
   - 文件位置：`~/Desktop/LINKEDIN/`

2. **LinkedIn业务信息采集系统**
   - 基于bababot方法（实际数据优先）
   - 只保留真实LinkedIn帖子数据
   - 总表：`~/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv`
   - 当前真实数据：9条高质量记录

3. **RFQ Inquiry Trial (进行中)**
   - 项目时间: 2025-07-09 启动
   - 任务状态: 已进入自动提交流程（按有效Condition筛选并以“RFQ SENT/成功回执”为准）
   - 最新进展（2026-03-01）:
     * 1152466-250：已成功提交（AERO-ZONE, SV）
     * 129666-3：已成功提交（AERONED BV, NE）
     * 10037-0770：按前10家有效供应商持续执行中（不足10家则按实际有效数）
   - 零件号:
     * 10037-0770 (Fuel Load Preselect Indicator Assembly): 80个供应商，市价~$6,000
     * 1152466-250 (APU Start Converter Unit): 95个供应商，市价~$78,650
     * 129666-3 (Precooler Control Valve Sensor): 108个供应商，市价~$1,000-5,000
   - 供应商总数: 283+
   - 文件位置: `rfq_inquiry_progress.md`

4. **自动化工作流程**
   - WORKFLOW_AUTO.md 定义标准流程
   - 心跳检查定期维护系统健康
   - GitHub同步保存所有工作成果
   - Browser Relay监控: 自动检测断开/恢复（当前以watchdog机制为主）

### 重要偏好
- **数据真实性至上**：只保留真实LinkedIn帖子，删除所有模拟数据
- **业务导向**：所有分析围绕航材、发动机、起落架、飞机整机业务展开
- **效率优先**：快速响应，直接给出 actionable insights
- **文件管理**：桌面文件夹为主存储，GitHub为备份
- **表格软件偏好**：默认使用 WPS 打开所有表格文件

### 技术栈
- OpenClaw + Browser Relay 进行LinkedIn数据采集
- Python脚本进行批量分析和数据处理
- Excel/CSV进行数据管理和汇总
- GitHub进行版本控制和备份

### 当前关注点
1. 修复Browser Relay稳定性问题，获取更多真实LinkedIn数据
2. 验证专业推断分析的准确性
3. 将分析结果转化为实际业务联系
4. 建立更稳定的技术基础设施

### 沟通习惯
- 直接下达任务指令
- 重视结果而非过程描述
- 对航空行业专业术语熟悉
- 偏好中文交流

---
_Last updated: 2026-03-01_
