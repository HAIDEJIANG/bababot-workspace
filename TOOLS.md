# TOOLS.md - Local Notes
Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here
Things like:

Camera names and locations
SSH hosts and aliases
Preferred voices for TTS
Speaker/room names, Device nicknames, Anything environment-specific

## Examples
```markdown

### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?
Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Email Accounts Configuration

| 邮箱地址 | 用途 | 主要场景 |
|---------|------|---------|
| **jianghaide@gmail.com** | 客户询价接收 | 海特高新日常询价、AVAIR 等国外客户沟通 |
| **sale@aeroedgeglobal.com** | 供应商报价接收 | 接收供应商报价、沟通报价内容 |
| **jianghaide@aeroedgeglobal.com** | 特定项目联系 | 联系特定客户或特定项目，有特定目的 |

### IMAP/SMTP 配置
- Gmail: imap.gmail.com:993 (TLS) / smtp.gmail.com:587 (STARTTLS)
- 163 Enterprise: imaphz.qiye.163.com:993 (TLS) / smtp.163.com:465 (SSL)

---

---

## Himalaya (邮件 CLI)

- **安装路径**: `C:\Users\Haide\.local\bin\himalaya.exe`
- **配置文件**: `C:\Users\Haide\.config\himalaya\config.toml`
- **密码文件**: `C:\Users\Haide\.config\himalaya\.imap_pw`
- **使用前需设 PATH**: `$env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"`

### 已配置账号: sale
- 邮箱: sale@aeroedgeglobal.com
- IMAP: imaphz.qiye.163.com:993 (TLS)
- SMTP: smtp.163.com:465 (TLS)
- 认证: 163 企业邮箱授权码 (存于密码文件)

### 常用命令
```powershell
# 列出最新邮件
himalaya envelope list --account sale --page-size 20

# 搜索邮件
himalaya envelope list --account sale --query "subject:RFQ"

# 读邮件
himalaya message read --account sale <message_id>

# 下载附件
himalaya attachment download --account sale <message_id>
```

---

Add whatever helps you do your job. This is your cheat sheet.