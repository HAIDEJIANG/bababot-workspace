# MEMORY.md - 长期记忆

[固定] 本文件用于存储需要长期保留的重要信息、偏好、约定和反复出现的问题。以「[固定]」开头的段落不要修改。

---

## 🔧 技术配置

### Browser Relay 权限规则
- 如果 `~/.openclaw/openclaw.json` 中存在 `plugins.allow` 数组，必须显式添加 `"browser"` 才能启用浏览器控制
- `plugins.allow` 不存在时，所有插件默认启用
- 此规则在配置向导中不会提示，错误信息 "not allowed" 不指向具体原因
- 修复方法：编辑 `openclaw.json`，添加 `"browser"` 到 `plugins.allow` 列表

### LinkedIn 采集策略
- **铁律：只用 Feed 滚动采集，绝不使用搜索模式**（用户多次强调）
- Feed 内容重复时结束采集，不切换搜索
- 采集输出目录：`C:/Users/Haide/Desktop/real business post/`
- Master Table 使用追加模式（`'a'`），避免覆盖历史数据
- 系统自动备份为 `_old.csv` 文件

### CDP 协议限制
- LinkedIn 使用 Shadow DOM 隔离，CDP 的 `document.querySelectorAll()` 无法穿透
- 动态类名哈希（如 `_4de8b190`）每次页面加载都不同
- 不推荐使用 CDP 协议采集 LinkedIn 内容

---

## 📋 业务流程

### RFQ 自动化发送
- 脚本：`stockmarket_rfq.py v3`
- 条件筛选：New (FN/NE/NS), SV (OH/RP/SV)
- 去重逻辑：同一供应商只发送一次
- 输出文件：`rfq_auto_results_YYYYMMDD_HHMMSS.csv`
- 海特询价截止日期通常为发出后 7 天

### 邮件配置
- 客户询价接收：jianghaide@gmail.com
- 供应商报价接收：sale@aeroedgeglobal.com (163 企业邮箱)
- 特定项目联系：jianghaide@aeroedgeglobal.com
- Himalaya CLI 已配置 sale 账号

---

## 💡 诊断方法论

**深层诊断原则：**
1. 错误信息模糊时，打开配置文件逐项检查
2. 查阅官方文档是关键——有些规则只在文档中说明
3. 从"服务为什么不启动"下探到"权限为什么被拒绝"

**诊断层次：**
- 服务层 → 认证层 → 配置层 → 文档层

---

## 🤖 主动优化原则

**处理数据类任务时，主动交付干净结果：**
1. **去重** - 避免重复记录浪费时间筛选
2. **清理无效数据** - 删除网页元素、空记录等污染数据
3. **整合分散文件** - 合并多个来源为一个干净、可用的数据源
4. **质量统计** - 汇报数据质量指标（公司数、联系方式数等）

**核心理念：** 用户说的是"合并"，理解应该是"整理出一个干净、可用的数据源"。能做的就顺手做了，不用事事问。

---

## ✈️ LinkedIn 联系人筛选规则（2026-03-31 教训）

**Bill Elder 事件教训：** B777/B787 Fleet Training Manager 与 V2500 发动机无关

**筛选铁律：**
1. ✅ 检查当前职位是否涉及目标发动机/机型（V2500 → A320 系列）
2. ✅ 检查工作经验是否与目标业务领域相关
3. ✅ 公司名称是目标运营商，但要结合职位判断
4. ❌ 不能只看 "Fleet" 字样就发送

**发动机/机型对应速查：**
| 发动机 | 适用机型 | 备注 |
|--------|----------|------|
| V2500 | A320 系列 (A319/A320/A321) | 目标发动机 |
| CFM56 | A320 系列, B737NG | 竞争发动机 |
| LEAP | A320neo, B737MAX | 新一代 |
| GE90/GEnx | B777/B787 | ❌ 与 V2500 无关 |
| Trent XWB | A350 | ❌ 与 V2500 无关 |

---

## 📝 Memory 文件操作铁律（2026-03-31 教训）

**错误类型：** 误用 write 覆盖 memory 文件（连续多次）

**正确流程：**
1. ✅ 先 read 现有内容
2. ✅ 合并原有 + 新增内容
3. ✅ write 完整内容（原有 + 新增）
4. ❌ 绝不可直接 write 覆盖已有文件

**根本原因：** write 工具是覆盖式写入，必须先获取原内容再合并

---

## 📊 LinkedIn Feed 采集性质

**Feed 采集特点：**
- ✅ 长期持续运行 - Cron 定时任务（每 4 小时）
- ✅ 增量追加数据 - 每次采集结果追加到 Master Table
- ❌ 无进度百分比概念 - 不存在"完成目标"，持续运行中

**心跳报告正确表示：**
- ✅ Cron 定时运行中（每 4 小时执行）
- ✅ 增量追加到 Master Table（数据持续增长）
- ❌ 不显示进度百分比（Feed 采集无完成目标）

---

## ⏰ 任务调度规则

| 任务类型 | 夜间行为 (23:00-08:00) | 原因 |
|----------|----------------------|------|
| 心跳检查 | 静默 | 节省资源、避免打扰 |
| 信息采集 | 全天运行 | 业务需要，不可中断 |

---

## 📊 业务数据

### LinkedIn Master Table
- 文件位置：`C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv`
- 只保留真实 LinkedIn 帖子数据，删除所有模拟数据
- 2026-03-31 合并后总计 **998 条有效记录**
- 覆盖 362 家公司/发布者，328 条有联系方式
- 脚本使用追加模式，自动备份为 `_old.csv`

### 高优先级业务线索类型
- AOG (Aircraft On Ground) 紧急需求 - 最高优先级
- 发动机销售/采购 (CFM56, V2500, PW 系列)
- 起落架销售/租赁/维修
- 飞机整机销售/采购 (A320neo, B737 等)
- MRO 服务

---

*最后更新：2026-04-01 01:00*

---

## 🔧 RFQ 数据提取方法（2026-04-01 新增）

**铁律：从 Gmail 预览页面直接提取表格数据，不下载 Excel 文件！**

**操作流程**：
1. 打开 Gmail 邮件 → 点击附件预览（不是下载）
2. 预览页面包含完整表格内容（所有零件数据）
3. 用 browser 工具 `evaluate` 函数提取 `document.body.innerText`
4. Python 解析文本 → 按制表符分割 → 提取 序号/PN/条件/数量
5. 生成 CSV 文件：`序号，件号，条件，数量`

**成功案例**：RFQ20260401-01（33 个 PN，83 条 RFQ 发送）

---

## 🌐 Browser 工具采集 LinkedIn 方法（2026-04-01 新增）

**CDP WebSocket Origin 问题**：
- Edge 浏览器 WebSocket 连接需要 `--remote-allow-origins=*` 参数
- 当前 OpenClaw 浏览器启动配置未包含此参数
- 错误信息：`Handshake status 403 Forbidden`

**临时解决方案**：使用 browser 工具直接采集
```javascript
// 滚动页面
browser(action="act", kind="evaluate", fn="() => { window.scrollBy(0, 2000); return 'scrolled'; }")

// 提取帖子内容
browser(action="act", kind="evaluate", fn="() => { return document.body.innerText; }")
```

**永久修复**：修改 OpenClaw 浏览器启动配置添加 `--remote-allow-origins=*` 参数

---

## 📸 EasyOCR 图片分析（2026-04-01 新增）

**安装位置**：Python 环境 + `~/.EasyOCR/model/`

**支持语言**：`['en', 'ch_sim']` (英文 + 简体中文)

**使用场景**：当 OpenClaw image 工具不可用时（模型 API key 未配置），使用 EasyOCR 进行本地 OCR 分析

**使用方式**：
```python
import easyocr
reader = easyocr.Reader(['en', 'ch_sim'])
result = reader.readtext(image_path)
```

---

## 📊 V2500 LinkedIn Connect 任务记录（2026-04-01）

**任务规模**：47 个运营商，约 370 位联系人

**最高价值联系人 TOP 5**：
1. Kwang Eun (Charlie) Kim - Korean Air Managing VP - Engine Maintenance Center
2. Abraham Thomas - Air India Head-Powerplant
3. Yosuke Kinoshita - ANA Engine Technics VP Maintenance
4. Xin Li - CAAC SAACC Director of Powerplant Division
5. Gustavo Merizalde - ex-AerCap/ILFC VP Technical Services

**发送规则**：统一使用 "Send without a note"，遇到 LinkedIn 每周限额时停止
