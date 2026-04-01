# Daily Learnings - 2026-03-30

## ClawHub Skill Market 调研

**来源**: https://clawhub.ai/skills?nonSuspicious=true

**核心发现**:
- ClawHub 目前处于早期阶段，技能市场尚未有大量内容
- 页面显示 "Loading skills…" 和 "No skills yet. Be the first."
- 平台支持技能版本管理、向量搜索、一键安装
- 安全标记功能：可筛选 nonSuspicious=true 的技能
- 当前无高安装量技能可供推荐

**与当前工作相关性**: ⚠️ 低 - 市场尚未成熟，暂无可安装的技能推荐

**建议**: 可关注 ClawHub 后续发展，待技能生态成熟后再评估安装

---

## YouTube OpenClaw 视频 (近 7 天)

### 1. OpenClaw v2026.3.28 更新说明
**来源**: https://www.youtube.com/watch?v=SYjmAn5OwgY
**发布日期**: 2026-03-28 (最新)
**核心要点**: 
- 95 次提交，71+ 贡献者，60+ bug 修复
- 新功能：xAI Responses API 支持 x_search、工具审批工作流 (hooks)、MiniMax 图像支持
**与当前工作相关性**: ✅ 高 - 工具审批功能与当前安全策略相关，可参考优化

### 2. OpenClaw v2026.3.24 更新说明
**来源**: https://www.youtube.com/watch?v=ZMGkThq933g
**发布日期**: 2026-03-24
**核心要点**:
- 14 项重大变更，包括完整 Microsoft Teams SDK 迁移 (支持流式传输)
- 新增 Docker 容器支持、OpenAI 兼容 API
**与当前工作相关性**: ⚠️ 中 - Docker 支持可能对部署架构有影响

### 3. OpenClaw v2026.3.23 更新说明
**来源**: https://www.youtube.com/watch?v=WR6972yEA4I
**发布日期**: 2026-03-23
**核心要点**:
- UI 增强、安全改进
- 具体细节需观看视频获取
**与当前工作相关性**: ⚠️ 中 - 安全改进可能影响当前配置

### 4. OpenClaw 教程类视频 (多个)
**来源**: 多个 YouTube 教程视频
**核心要点**: 2026 年 OpenClaw 设置和使用教程，涵盖基础配置、自动化任务、实际用例
**与当前工作相关性**: ⚠️ 低 - 基础内容，当前配置已超越入门阶段

---

## 总结

**今日学习重点**:
1. ClawHub 技能市场尚在早期，暂无推荐技能
2. OpenClaw 近期更新频繁 (一周内 3 个版本)，重点关注工具审批工作流和 xAI 搜索集成
3. 建议关注官方更新日志，评估是否升级至 v2026.3.28

**下一步行动**:
- 无立即行动项
- 可持续监控 ClawHub 技能市场成熟度
- 考虑评估 v2026.3.28 的工具审批功能是否值得升级

---
---

# Daily Learnings - 2026-03-31

## ClawHub Skill Market 推荐列表

**来源**: https://clawhub.ai
**筛选标准**: 安装量靠前、无安全风险标记、与航空航材/业务自动化相关

### 🌟 Highlighted Skills (官方推荐)

| Skill | 作者 | 评分 | 安装量 | 简介 | 相关性 |
|-------|------|------|--------|------|--------|
| **X Search** | @jaaneek | ⭐47 | 5.3k | 使用 xAI API 搜索 X/Twitter 帖子 | ⚠️ 低 - 社交媒体搜索，与当前业务关联有限 |
| **Trello** | @steipete | ⭐118 | 31k | 通过 REST API 管理 Trello 看板/列表/卡片 | ⚠️ 中 - 项目管理工具，可追踪 RFQ 进度 |
| **Slack** | @steipete | ⭐110 | 34.3k | 从 Clawdbot 控制 Slack (消息/反应/固定) | ⚠️ 低 - 团队沟通，当前用 Telegram |
| **CalDAV Calendar** | @asleep123 | ⭐187 | 23.1k | 同步 CalDAV 日历 (iCloud/Google/Fastmail) | ⚠️ 中 - 日历集成，可补充现有日程管理 |
| **Answer Overflow** | @rhyssullivan | ⭐139 | 15.2k | 搜索 Discord 社区技术讨论 | ⚠️ 低 - 技术问答，与航材业务关联有限 |

### 🔥 Popular Skills (高安装量)

| Skill | 作者 | 评分 | 安装量 | 简介 | 相关性 |
|-------|------|------|--------|------|--------|
| **self-improving-agent** | @pskoett | ⭐2.9k | **330k** | 捕获学习/错误/修正，实现持续改进 | ✅ **高** - 可优化 Agent 自动决策能力 |
| **ontology** | @oswalpalash | ⭐428 | **143k** | 结构化知识图谱 (人员/项目/任务/文档) | ✅ **高** - 可管理供应商/客户/零件关系 |
| **Self-Improving + Proactive Agent** | @ivangdavila | ⭐759 | **131k** | 自我反思 + 自我批评 + 自组织记忆 | ✅ **高** - 增强 Agent 主动性和准确性 |
| **AdMapix** | @fly0pants | ⭐207 | 77.8k | 广告情报与应用分析 | ⚠️ 低 - 营销分析，与航材交易关联有限 |
| **Nano Banana Pro** | @steipete | ⭐291 | 73.2k | Gemini 3 Pro 图像生成/编辑 | ⚠️ 低 - 图像创作，非核心业务需求 |
| **Obsidian** | @steipete | ⭐280 | 69.7k | 操作 Obsidian 知识库 (Markdown) | ✅ **中** - 知识管理，可整合业务文档 |
| **Baidu Search** | @ide-rea | ⭐175 | 67.4k | 百度 AI 搜索引擎 | ⚠️ 低 - 已有 web_search 工具 |
| **API Gateway** | @byungkyu | ⭐290 | 58.8k | 连接 100+ API (Google/Microsoft/GitHub 等) | ✅ **中** - 可扩展业务系统集成 |
| **Agent Browser** | @matrixy | ⭐196 | 57.7k | 无头浏览器自动化 (可访问性树快照) | ✅ **高** - 与当前 Browser Relay 功能互补 |
| **Mcporter** | @steipete | ⭐147 | 49k | MCP 服务器/工具 CLI | ⚠️ 中 - 工具扩展，需评估具体 MCP 服务 |
| **Word / DOCX** | @ivangdavila | ⭐180 | 42k | 创建/编辑 Word 文档 (样式/修订/表格) | ✅ **中** - RFQ 文档/报价单生成 |
| **Excel / XLSX** | @ivangdavila | ⭐143 | 37.1k | 创建/编辑 Excel 工作簿 (公式/格式) | ✅ **中** - 供应商报价表/数据分析 |

### 📋 推荐优先级 (待用户确认)

**🟢 强烈推荐 (与当前业务高度相关):**
1. **self-improving-agent** (330k installs) - 提升 Agent 自动决策准确性，减少人工干预
2. **ontology** (143k installs) - 结构化存储供应商/客户/零件号/交易记录
3. **Self-Improving + Proactive Agent** (131k installs) - 增强主动性和自我纠错

**🟡 值得考虑 (有实用价值):**
4. **Agent Browser** (57.7k installs) - 补充 Browser Relay，可能提升 LinkedIn 采集稳定性
5. **Excel / XLSX** (37.1k installs) - 直接生成/编辑报价表格，减少手动操作
6. **API Gateway** (58.8k installs) - 未来扩展业务系统集成的基础

**⚪ 暂不推荐 (关联度低或已有替代):**
- X Search, Slack, AdMapix, Nano Banana Pro, Baidu Search 等

---

## YouTube OpenClaw 视频 (近 7 天)

### 1. The only OpenClaw tutorial you'll ever need (March 2026 edition)
**来源**: https://www.youtube.com/watch?v=CxErCGVo-oo
**核心要点**: 完整版 OpenClaw 指南，涵盖构建 AI 员工的全流程，包含 Vibe Coding Academy 训练营内容
**与当前工作相关性**: ⚠️ 中 - 教程类内容，当前配置已超越入门阶段

### 2. How To Build OpenClaw Multi-Agent AI Team in 2026
**来源**: https://www.youtube.com/watch?v=_crWwyHuZ2E
**核心要点**: 2026 年增长最快的开源 AI Agent，教程展示如何设置多 Agent 系统自动化销售和营销工作
**与当前工作相关性**: ✅ **高** - 多 Agent 架构可参考用于 RFQ 自动提交/供应商分析分工

### 3. OpenClaw Tutorial For Beginners (2026)
**来源**: https://www.youtube.com/watch?v=Gc4fyY0_8Rc
**核心要点**: 从零开始的分步教程，涵盖设置、主要功能、自动化任务和实际用例
**与当前工作相关性**: ⚠️ 低 - 基础入门内容

### 4. How To Use Open Claw For Beginners (Full 2026 Guide)
**来源**: https://www.youtube.com/watch?v=BxBQJQvMf_E
**核心要点**: 2026 完整指南，简单易懂的分步讲解
**与当前工作相关性**: ⚠️ 低 - 基础入门内容

### 5. OpenClaw Setup Tutorial With New Usecases (2026)
**来源**: https://www.youtube.com/watch?v=1c_9tuQdkLY
**核心要点**: 新用例展示，由 TheAIGRID 频道发布 (390K 订阅)
**与当前工作相关性**: ⚠️ 中 - 可能包含新的自动化模式参考

### 6. My AI Agents Made Money in 7 Days (OpenClaw)
**来源**: https://blockchain-pro.com/my-ai-agents-made-money-in-7-days-openclaw/2026/03/26/
**核心要点**: 实际案例：给 3 个 AI Agent 各$1000，7 天后的收益结果 (2026-03-26 发布)
**与当前工作相关性**: ✅ **中** - 可参考 Agent 商业化/自动化变现思路

---

## 总结

**今日学习重点**:
1. **ClawHub 技能市场已成熟** - 有超过 12 个高安装量技能 (30k-330k installs)，无安全风险标记
2. **多 Agent 架构是趋势** - YouTube 最新视频强调多 Agent 分工协作自动化销售/营销
3. **自我改进型 Agent 最受欢迎** - self-improving-agent 以 330k 安装量居首，说明用户重视 Agent 持续优化能力

**与当前业务关联**:
- ✅ 航材交易自动化可借鉴多 Agent 分工 (RFQ 提交/供应商分析/报价对比)
- ✅ Ontology 技能可结构化管理 3,185 位 LinkedIn 联系人和供应商关系
- ✅ Excel/Word 技能可直接生成 RFQ 文档和报价分析表

**下一步行动 (待确认)**:
- 评估是否安装 self-improving-agent 提升当前 RFQ 自动提交准确性
- 考虑 ontology 技能整合 LinkedIn 联系人分析和供应商数据
- 研究多 Agent 架构优化现有 Browser Relay + 数据分析流程

---
---

# Daily Learnings - 2026-04-01

## ClawHub Skill Market 推荐列表

**来源**: https://clawhub.ai
**调研时间**: 2026-04-01 03:00 HKT
**筛选标准**: 安装量靠前、无安全风险标记、与航空航材业务/Agent 设定相关

### 🌟 Highlighted Skills (官方精选)

| Skill | 作者 | 评分 | 安装量 | 简介 | 相关性 |
|-------|------|------|--------|------|--------|
| X Search | @jaaneek | ⭐47 | 5.8k | 使用 xAI API 搜索 X/Twitter 帖子 | ⚠️ 低 |
| Trello | @steipete | ⭐119 | 31.3k | 管理 Trello 看板/列表/卡片 | ⚠️ 中 - 可追踪 RFQ 进度 |
| Slack | @steipete | ⭐112 | 34.7k | 从 Clawdbot 控制 Slack | ⚠️ 低 - 当前用 Telegram |
| CalDAV Calendar | @asleep123 | ⭐188 | 23.3k | 同步 CalDAV 日历 | ⚠️ 中 |
| Answer Overflow | @rhyssullivan | ⭐139 | 15.3k | 搜索 Discord 技术讨论 | ⚠️ 低 |

### 🔥 Popular Skills (按安装量排序)

| Skill | 作者 | 评分 | 安装量 | 简介 | 相关性 |
|-------|------|------|--------|------|--------|
| **self-improving-agent** | @pskoett | ⭐2.9k | **336k** | 捕获学习/错误/修正，持续改进 | ✅ 高 |
| **ontology** | @oswalpalash | ⭐434 | **144k** | 结构化知识图谱 (人员/项目/任务/文档) | ✅ 高 |
| **Self-Improving + Proactive Agent** | @ivangdavila | ⭐765 | **134k** | 自我反思 + 自我批评 + 自组织记忆 | ✅ 高 |
| AdMapix | @fly0pants | ⭐208 | 78.1k | 广告情报与应用分析 | ⚠️ 低 |
| Nano Banana Pro | @steipete | ⭐294 | 74.4k | Gemini 3 Pro 图像生成/编辑 | ⚠️ 低 |
| **Obsidian** | @steipete | ⭐283 | 70.6k | 操作 Obsidian 知识库 | ✅ 中 |
| Baidu Search | @ide-rea | ⭐178 | 68.5k | 百度 AI 搜索引擎 | ⚠️ 低 |
| **Agent Browser** | @matrixy | ⭐206 | 60k | 无头浏览器自动化 | ✅ 高 |
| **API Gateway** | @byungkyu | ⭐291 | 59.6k | 连接 100+ API | ✅ 中 |
| Mcporter | @steipete | ⭐148 | 49.6k | MCP 服务器 CLI | ⚠️ 中 |
| **Word / DOCX** | @ivangdavila | ⭐187 | 43.8k | 创建/编辑 Word 文档 | ✅ 中 |
| **Excel / XLSX** | @ivangdavila | ⭐145 | 38.8k | 创建/编辑 Excel 工作簿 | ✅ 中 |

### 📋 推荐优先级 (待用户确认)

**🟢 强烈推荐 (与航材业务高度相关):**
1. **self-improving-agent** (336k installs) - 提升 RFQ 自动提交准确性，减少人工纠错
2. **ontology** (144k installs) - 结构化管理 3,185 位 LinkedIn 联系人 + 283+ 供应商关系网
3. **Self-Improving + Proactive Agent** (134k installs) - 增强主动性和自我纠错能力

**🟡 值得考虑 (有实用价值):**
4. **Agent Browser** (60k installs) - 补充 Browser Relay，可能提升 LinkedIn 采集稳定性
5. **Excel / XLSX** (38.8k installs) - 直接生成供应商报价分析表
6. **API Gateway** (59.6k installs) - 未来扩展业务系统集成的基础

**⚪ 暂不推荐:**
- X Search, Slack, AdMapix, Nano Banana Pro, Baidu Search 等与当前业务关联度低

---

## YouTube OpenClaw 视频 (近 7 天搜索)

**搜索来源**: DuckDuckGo (site:youtube.com OpenClaw 2026)

### 找到的视频列表:

| 标题 | 链接 | 相关性 |
|------|------|--------|
| OpenClaw Tutorial for Beginners: How to Use & Set up OpenClaw | https://www.youtube.com/watch?v=IH9pnx5W2T4 | ⚠️ 低 - 入门教程 |
| OpenClaw 2026: The Ultimate Easy Setup Guide | https://www.youtube.com/watch?v=K97gSYDw5hQ | ⚠️ 低 - 入门教程 |
| The only OpenClaw tutorial you'll ever need (March 2026 edition) | https://www.youtube.com/watch?v=CxErCGVo-oo | ⚠️ 中 - 完整指南 |
| How To Use Open Claw For Beginners (Full 2026 Guide) | https://www.youtube.com/watch?v=BxBQJQvMf_E | ⚠️ 低 - 入门教程 |
| OpenClaw: Complete Beginners Guide! (2026) | https://www.youtube.com/watch?v=BI034QtdmTo | ⚠️ 低 - 入门教程 |
| OpenClaw Tutorial (2026) | Everything you need to know! | https://www.youtube.com/watch?v=znaJgKDo-oI | ⚠️ 中 - 功能概览 |
| OpenClaw Tutorial For Beginners (2026) | How to Use OpenClaw | https://www.youtube.com/watch?v=Gc4fyY0_8Rc | ⚠️ 低 - 入门教程 |
| OpenClaw Tutorial: How to Run a Local AI Agent (2026 Guide) | https://www.youtube.com/watch?v=StKBpXSf08E | ⚠️ 中 - 本地部署 |
| OpenClaw Setup Tutorial With New Usecases (2026) | https://www.youtube.com/watch?v=1c_9tuQdkLY | ✅ 中 - 新用例 (TheAIGRID 390K 订阅) |
| Ubuntu OpenClaw Setup: From Zero to Running | 2026 | Full Guide | https://www.youtube.com/watch?v=hvMoz3hRybk | ⚠️ 低 - Linux 特定 |

**核心要点总结**:
- 搜索结果以入门教程为主，大多数为"Beginner Guide"类型
- 唯一值得关注的是 TheAIGRID 频道的"New Usecases"视频 (390K 订阅，可能包含新自动化模式)
- 无法从搜索结果确认具体发布日期，需进一步访问视频页面验证是否为近 7 天内容
- 无官方更新日志类视频 (对比昨日调研，今日未发现 v2026.3.28 等版本更新内容)

**与当前工作相关性**: ⚠️ **低-中** - 当前配置已超越入门阶段，主要价值在于发现新用例参考

---

## 总结

**今日学习重点**:
1. **ClawHub 技能市场稳定** - 与昨日数据基本一致，Top 技能安装量在 38k-336k 区间，无安全风险标记
2. **YouTube 内容以教程为主** - 近 7 天未发现官方更新日志视频，多为入门级教程内容
3. **推荐技能方向明确** - self-improving-agent (336k)、ontology (144k)、Agent Browser (60k) 与当前航材业务自动化需求匹配度高

**与当前业务关联**:
- ✅ self-improving-agent 可优化 RFQ 自动提交的准确率
- ✅ ontology 可整合 LinkedIn 3,185 位联系人 + 283+ 供应商数据
- ✅ Agent Browser 可能补充/替代当前 Browser Relay 方案

**下一步行动 (待用户确认)**:
- 是否安装 self-improving-agent 测试 RFQ 自动提交优化效果
- 是否安装 ontology 重构联系人/供应商数据存储结构
- 是否安装 Agent Browser 对比与 Browser Relay 的稳定性差异
