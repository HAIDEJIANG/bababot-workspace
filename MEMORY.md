# MEMORY.md - 长期记忆

## 关于 Haide
- **身份**: 航空业务人士
- **时区**: Asia/Shanghai (北京时间)
- **行业**: 航空发动机售后市场（租赁、MRO、融资、经纪）

## 常用工具 & 平台
- **LinkedIn**: 主要社交网络，人脉集中在航空领域
- **StockMarket.aero**: 航材库存查询和 RFQ 发送
- **GitHub**: 私人仓库用于同步 bababot workspace

## 经验教训 & 优化 (Lessons Learned)
- **Browser Relay 自动断连**: StockMarket.aero 在发送 RFQ 后会触发页面重载，导致浏览器扩展（龙虾图标）自动断开。
    - **修复 (2026-02-06)**: 已修改 `background.js` 源码，增加了“自动重连”逻辑。如果不是用户手动关闭，插件会在断开 1 秒后尝试自动重新附加。
    - **注意**: 需要在 `chrome://extensions` 页面点击“刷新 (Reload)”按钮使改动生效。

## 工作习惯
- 会让我帮忙查航材库存、发 RFQ
- LinkedIn 人脉分析
- 浏览器自动化任务
- **领英航材发现系统**：
    - 已配置自动化脚本 `scripts/linkedin_lead_gen.py`，使用 LinkdAPI 搜索核心关键词。
    - 监控关键词：`CFM56-7B`, `LEAP`, `GE90`, `Trent 700`, `V2500`。
    - 已设置 Cron 任务，每日北京时间 09:00 和 21:00 自动执行并报告。
- **麦当劳自动领券**：
    - 已配置每日自动领券脚本 `scripts/mcd_claim.js`。
    - 已设置 Cron 任务，每日北京时间 09:30 自动触发领券并报告结果。
    - Token 归属于 Haide，已加密保存在脚本中。
- **快捷指令： “同步记忆”**
    - 触发动作：
        1. 将当前及历史聊天记录（.jsonl 文件）从系统目录备份至工作区的 `chat_backups/` 文件夹。
        2. 将整个工作区（包含记忆文件、配置及聊天备份）推送到 GitHub 私人仓库 (`HAIDEJIANG/bababot-workspace`)。
    - 目的：确保本地和云端的数据一致性及安全性。
- **快捷指令： “请刷新领英”**
    - 触发动作：浏览 `https://www.linkedin.com/feed/`。
    - 任务要求：筛选并总结最新的 **30 条** 与 **航材、飞机整机、起落架、APU 或发动机** 相关的帖子。
    - 信息包含：发帖人姓名、公司名、职务、联系方式、发帖时间、帖子的文字网址链接 (Raw Text URL)、帖子汇总内容。

## 重要配置
- LinkdAPI KEY 已配置在 TOOLS.md
- Chrome 扩展位置: `C:\Users\Haide\AppData\Roaming\npm\node_modules\openclaw\assets\chrome-extension`

## 历史记录
- **2026-02-04**: 分析了 LinkedIn 10个新连接；StockMarket.aero 查询多个 PN；发送 RFQ (3800454-6)；安装 130+ 技能
- **2026-02-05**: 从 GitHub 同步 workspace；安装 memU 记忆系统；指导安装浏览器扩展
- **2026-02-06**: 完成了 Excel 表格中全部 **154个 PN** 的库存大搜索，记录了详细的供应商与库存数据。

