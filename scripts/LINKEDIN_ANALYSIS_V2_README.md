# LinkedIn 联系人分析优化版 - 启动说明

## 📋 优化内容

### v2 优化版新增功能
1. **更频繁的进度保存** - 每 10 个联系人保存一次（原 50 个）
2. **失败自动重试** - 最多重试 3 次，带退避延迟
3. **增强的错误处理** - 区分超时、失败、无帖子
4. **定期进度报告** - 每 100 个联系人生成 Markdown 报告
5. **自动恢复** - 从中断点继续执行

## 🚀 启动方式

### 方式 1：手动启动（推荐测试）

```powershell
# 1. 确保 Browser Relay 已启动（浏览器监听 9222 端口）
# 2. 运行脚本
cd C:\Users\Haide\.openclaw\workspace\scripts
python contact_deep_analysis_v2_optimized.py
```

### 方式 2：通过 cron 自动启动

cron 配置已存在，会自动检测并使用新脚本。

## 📊 监控进度

### 实时查看进度
```powershell
# 查看最新日志
Get-Content C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\analysis_log_*.txt -Tail 50

# 查看进度 JSON
python -c "import json; print(json.dumps(json.load(open('C:/Users/Haide/Desktop/LINKEDIN/ANALYSIS_20260326/progress.json')), indent=2, ensure_ascii=False))" | Select-Object -First 20
```

### 查看进度报告
```powershell
# 打开最新报告
code C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\progress_report_*.md
```

## 📁 输出文件

| 文件 | 说明 |
|------|------|
| `progress.json` | 实时进度（每 10 个联系人更新） |
| `analysis_log_*.txt` | 详细日志 |
| `progress_report_*.md` | 定期进度报告（每 100 个联系人） |
| `final_report.md` | 最终报告 |
| `contact_profiles_full.csv` | 联系人档案 |
| `contact_posts_90days.csv` | 帖子数据 |
| `business_leads.csv` | 业务线索 |

## ⚙️ 配置参数

在脚本顶部修改：

```python
PROGRESS_SAVE_INTERVAL = 10   # 进度保存间隔
REPORT_INTERVAL = 100         # 报告生成间隔
MAX_RETRY_ATTEMPTS = 3        # 重试次数
RETRY_BACKOFF_SECONDS = 5     # 重试退避时间
MIN_INTERVAL_SECONDS = 20     # 最小执行间隔
MAX_INTERVAL_SECONDS = 40     # 最大执行间隔
```

## 🛑 停止和恢复

### 停止
按 `Ctrl+C` 安全停止，进度会自动保存。

### 恢复
重新运行脚本，会自动从上次中断点继续。

## 📈 性能预估

基于当前进度（383/3185，12.03%）：
- 剩余：2,802 个联系人
- 预计速度：~100 联系人/小时
- 预计完成时间：~28 小时

---

*创建时间：2026-03-29 00:55*
