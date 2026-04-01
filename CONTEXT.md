# CONTEXT.md - 当前工作上下文

## 2026-04-01 关键摘要

1. **V2500 LinkedIn Connect 任务里程碑** - 累计发送约 370 位联系人，覆盖 47 个 V2500 运营商；最高价值联系人：Kwang Eun (Charlie) Kim (Korean Air Managing VP - Engine Maintenance Center)、Abraham Thomas (Air India Head-Powerplant)、Yosuke Kinoshita (ANA Engine Technics VP)、Xin Li (CAAC SAACC Director of Powerplant Division)

2. **RFQ20260401-01 海特高新询价完成** - 33 个 PN（全新件 26+ 可用件 7），发送 83 条 RFQ，22 个 PN 成功/7 个无库存/4 个条件不匹配；Gmail 预览页面直接提取表格方法验证成功（无需下载 Excel 文件）

3. **新技能安装 6 个** - self-improving-agent(336k, 提升 RFQ 准确性), ontology(144k, LinkedIn 联系人管理), self-improving-proactive-agent(134k), agent-browser-clawdbot(60k, Browser Relay 补充), api-gateway(59.6k), excel(38.8k)

4. **memU 每日提取运行** - OPENAI_API_KEY 未配置，embedding 步骤跳过，记忆文本已创建

## 2026-03-31 关键摘要

1. **V2500 LinkedIn Connect 任务完成** - 累计发送 114 位联系人，覆盖 Top 8 V2500 运营商（940 架飞机），包括 American Airlines 71 位、JetBlue 9 位、United Airlines 13 位、China Southern 3 位、China Eastern 2 位、Turkish Airlines 5 位、Wizz Air 7 位、IndiGo 4 位；核心高价值联系人包括机队交易总监、发动机采购经理、发动机维修总监、MRO 公司 CEO 等决策人

2. **OpenClaw 技能精简完成** - 从约 200 个技能精简到 20 个核心技能，删除约 180 个重叠/冗余技能；保留航空业务 (linkedin/gmail/browser-use/ddg-search/serper)、办公自动化 (n8n/paperless-ngx/excel/docx/pdf-form-filler)、系统核心 (basal-ganglia-memory/homeassistant)、其他 (moltr/frontend-design/remotion-video-toolkit/agentmail)

3. **心跳间隔调整完成** - 从 30 分钟改为 60 分钟，配置文件 openclaw.json 中 agents.defaults.heartbeat.every 已更新为 1h，Gateway 已重启使配置生效，活动时间窗口保持 08:00-23:00

4. **LinkedIn 联系人筛选规则教训** - Bill Elder 事件（B777/B787 Fleet Training Manager 与 V2500 无关），建立职位相关性筛选铁律：必须检查当前职位是否涉及目标发动机/机型、工作经验是否与目标业务领域相关、公司名称是否为目标运营商、不能只看 Fleet 字样就发送

5. **LinkedIn 采集铁律确认** - 用户多次强调只用 Feed 滚动采集，绝不使用搜索模式；Feed 内容重复时结束采集，不切换搜索；Feed 采集是长期持续运行工作，无进度百分比概念

## 2026-03-30 关键摘要

1. **Browser Relay 根本问题修复成功** - 发现 openclaw.json 中 plugins.allow 配置缺少 browser 权限，添加后浏览器控制完全恢复；教训：错误信息模糊时需打开配置文件逐项检查并查阅官方文档

2. **LinkedIn Feed 采集完成** - 35 分钟采集 17 条航材相关帖子，Master Table 总计 134 条；高优先级业务线索：Scott Hunstad 多个航材现货、Brian Nolan 紧急采购 A320neo、Kostantin 采购 CFM56-5B 发动机、IBA Group 3 架 A321-211P2F 货机出售

3. **RFQ20260330-01 海特询价任务完成** - 30 个 PN 处理完成，26 个发送成功，4 个无库存，总计约 156 条 RFQ 发送；脚本全流程自动化验证成功，等待供应商回复截止 April 6, 2026

4. **CDP 协议深度研究结论** - CDP 无法穿透 LinkedIn Shadow DOM 导致帖子提取失败；确认可行方案优先级：现有数据分析 > Playwright > Browser Relay 扩展 > CDP 协议

## 2026-03-29 关键摘要

1. **ClawTeam 多智能体框架安装完成** - Windows+WSL2 双环境配置，2.5 小时完成全部安装，tmux 后端支持已验证；功能包括团队创建/任务管理/Inbox 通信/git worktree 隔离/实时看板

2. **ClawTeam vs 原生 sub-agents 对比明确** - ClawTeam 优势：多 agent 并行/通信/任务依赖自动解锁/工作区隔离/无超时；劣势：Windows 需 WSL2 配置复杂；适用：复杂任务分解、多角色协作、长时间运行

3. **LinkedIn 联系人分析优化版已停止** - 进度 383/3,185(12%) 后终止，仅静态信息无动态帖子数据价值低；转向方案：用现有导出文件筛选 200-300 位高价值联系人精准联系

4. **RFQ Inquiry Trial 持续执行** - 1152466-250 和 129666-3 已成功提交，10037-0770 按前 10 家有效供应商持续执行，总计 283+ 供应商

## 2026-03-26 关键摘要

1. **LinkedIn 联系人优先级打分完成** - 3,185 位联系人全部打分，87% 高优先级（2,770 人），13% 中优先级（415 人）；输出 priority_ranking.csv

2. **LinkedIn 自动采集进行中** - 进度 11.7%（372/3,185），速度 65-90 人/小时，间隔 20-30 秒，预计 2 天完成；选择器问题已修复（多层备选方案）

3. **RFQ20260326-01 新询价单** - 海特高新 Cynthia Zhang 发送，截止 4 月 2 日；待下载附件解析零件清单并发送 StockMarket RFQ

4. **Scrapy 性能验证** - v2.14.2 安装成功，测试性能~545 条/分钟，用于 LinkedIn 数据采集

## 2026-03-25 关键摘要

1. **RFQ20260324-02 Batch 2 完成** - 10 个 PN 发送 15 条 RFQ，总计 114 条 RFQ 全部完成；6 个 PN 成功报价，3 个无库存，1 个条件不匹配（客户要全新件但市场只有 OH/SV）

2. **报价邮件处理系统建立** - 识别 11 封供应商报价回复，设计 Quotes_Master_Table.csv 总表（18 字段），himalaya+pymupdf 提取链路验证成功（无需 deepread 外部依赖）

3. **LinkedIn 采集两轮完成** - 扫描 100+ 帖子，提取 18 条高价值业务帖；关键发现：ERJ 起落架整套、CFM56-5B6 发动机 (fresh SV)、B747-400F 拆解、A330 MLG OH、Dash 8 Q400 整机

4. **技术工具链验证** - himalaya CLI v1.2.0 安装配置完成，pymupdf PDF 提取测试成功，openpyxl 就绪，gmail 技能需 maton.ai API key

5. **163 企业邮箱 IMAP 问题** - 需要授权码而非密码，浏览器 SPA 操作困难；需在 mail.qiye.163.com 设置中开启 IMAP 并生成授权码

## 2026-03-24 关键摘要

1. **RFQ20260324-02 海特高新询价启动** - Gmail 解析 2 个零件，PN1(796880-5-006) 向 7 家供应商发送询价，但条件匹配错误 (AR≠可用件)，任务 22:37 暂停

2. **条件匹配规则教训** - AR(As Removed) 是拆机件；可用件=SV/OH，全新件=NE/FN/NS，后续询价必须按此规则匹配

3. **StockMarket.aero 自动化不稳定** - 会话频繁过期致子代理停滞，fill 操作不生效需改用 type

## 历史关键事项

- **RFQ20260318-01** 42 项询价 100% 完成，已闭环
- **LinkedIn 采集系统** 运行稳定，39 条 + 高价值数据（21+18）
- **Browser Relay** 端口 18789，watchdog 机制监控（UTF-8 BOM 小问题非关键）
- **memU 记忆系统** 每日提取运行中（embedding 待配置 OPENAI_API_KEY）
- **报价总表** Quotes_Master_Table.csv 待建立（桌面）

---
最后更新：2026-04-01 23:00
当前行数：74 行
