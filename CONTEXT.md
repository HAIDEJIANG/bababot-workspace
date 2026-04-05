# CONTEXT.md - 当前工作上下文

## 2026-04-03 关键摘要

1. **LinkedIn Feed 采集两轮完成** - 08:18/12:18 两次采集共 12 条新帖子，主表累计 454 条记录；高价值线索：EREVEGLOBAL 多机型租赁 (C208/F50/DC9-34F/A321F/747F/CRJ-100)、B737-500 ACMI 租赁 (中东/非洲/亚洲)、Embraer 190-E2 制造进度 (2026 年 6 月交付)

2. **LinkedIn 采集脚本优化完成** - 添加 5 分钟周期刷新功能，解决 WebSocket 403 问题（Edge 添加 `--remote-allow-origins=*` 参数），效率显著提升（60 分钟采集~30 条，刷新 12 次）

3. **RFQ20260403-02 海特询价处理完成** - 42 个 PN，发送 173 条 RFQ，29 个 PN 成功/11 个无库存/2 个条件不匹配；截止日期 2026-04-13；自动化效率 936 条/小时（手动 1.5 条/小时）

4. **系统状态稳定** - Browser Relay 正常运行 (Edge, CDP Port 18800)，数据输出 CSV 格式 UTF-8 编码，无模拟数据全部真实 source_url 验证

## 2026-04-02 关键摘要

1. **B747F 销售任务 100% 完成** - 18:08-19:35 联系 118 位全球 B747F 运营商/管理公司/产权公司关键决策人，包括 Emirates VP Fleet Planning (Rogerio Leao)、Saudia VP Network Planning (Ricardo B.)、Boeing CEO (Lucky Cheong)、Airbus Head of Aircraft Trading (Pascal Dufour) 等高价值联系人，等待 LinkedIn 连接接受后私信 B747F 出售信息

2. **LinkedIn Feed 采集 3 轮完成** - 16:01/19:18/20:20 三次采集共 26 条新帖子，总表累计约 1300 条记录；高价值线索：CFM56-7B 采购需求 (kostantin@atg.aero, Fresh SV RC2500-3500)、Gulfstream G550 采购需求 (nate@aeroventures.com, 美国优先)、CFM56 被盗零件警告 (EASA 282 个零件流通致 737NG/A320ceo 停场风险)

3. **供应商报价提取完成** - 从 sale 邮箱处理 9 封报价邮件，下载 6 个 PDF 附件，提取 5 条新报价到 Quotes_Master_Table.csv（48 条总记录），包括 711002-5 ($5000 OH/JMF Global)、9DX404700-01 ($1100 NE/Tiger Enterprises)、Y580-02133-01-3 ($9650 NS/Pacific Aerospace)

4. **V2500 Connect 任务最终状态** - 累计发送约 370 位联系人覆盖 47 个 V2500 运营商，高价值联系人 75 位 (20%)，包括 Korean Air Managing VP (Kwang Eun Charlie Kim)、Air India Head-Powerplant (Abraham Thomas)、ANA Engine Technics VP (Yosuke Kinoshita)、CAAC SAACC Director (Xin Li)，任务 100% 完成等待连接接受

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

## 历史关键事项

- **RFQ20260318-01** 42 项询价 100% 完成，已闭环
- **LinkedIn 采集系统** 运行稳定，1300 条 + 高价值数据
- **Browser Relay** 端口 18800，watchdog 机制监控
- **memU 记忆系统** 每日提取运行中（embedding 待配置 OPENAI_API_KEY）
- **报价总表** Quotes_Master_Table.csv 48 条记录（桌面）

---
最后更新：2026-04-03 23:00
当前行数：55 行
