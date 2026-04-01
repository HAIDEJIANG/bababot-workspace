# OpenClaw 技能重叠分析报告

## 重叠技能分类（建议精简）

### 1. LinkedIn 相关（6个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| linkedin | ✅ 保留 | 主力技能，功能完整 |
| linkedin-automation | ❌ 删除 | 功能与 linkedin 重叠 |
| linkedin-automation-humanlike | ❌ 删除 | 特殊场景，可用 linkedin 替代 |
| linkedin-cli | ❌ 删除 | CLI 版本，browser 模式更优 |
| inkedin-automation-that-really-works | ❌ 删除 | 命名不规范，功能重叠 |
| linkdapi | ❌ 删除 | API 模式已弃用（见 MEMORY.md） |

### 2. 浏览器/自动化（12个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| browser-use | ✅ 保留 | 主力技能，通用浏览器自动化 |
| browser-use-skill | ❌ 删除 | 重复技能 |
| browser-cash | ❌ 删除 | 特殊用途，不常用 |
| browser-ladder | ❌ 删除 | 特殊用途 |
| clawbrowser | ❌ 删除 | 功能重叠 |
| playwright | ❌ 删除 | Playwright 已迁移到 CDP |
| playwright-cli | ❌ 删除 | 同上 |
| playwright-cli-openclaw | ❌ 删除 | 同上 |
| stealth-browser | ❌ 删除 | 功能已整合到 browser-use |
| kesslerio-stealth-browser | ❌ 删除 | 特殊版本 |
| fast-browser-use | ❌ 删除 | 速度优化版，可整合 |
| agent-browser | ❌ 删除 | 功能重叠 |

### 3. n8n 相关（5个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| n8n | ✅ 保留 | 主力技能 |
| n8n-api | ❌ 删除 | API 版本，功能已包含 |
| n8n-automation | ❌ 删除 | 功能重叠 |
| n8n-hub | ❌ 删除 | Hub 版本 |
| n8n-workflow-automation | ❌ 删除 | 功能重叠 |

### 4. 邮件相关（6个重叠 → 建议2个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| gmail | ✅ 保留 | Gmail 专用 |
| imap-smtp-email | ✅ 保留 | 通用邮件（配合 himalaya） |
| smtp-send | ❌ 删除 | 功能已包含在 imap-smtp-email |
| sendgrid-skills | ❌ 删除 | SendGrid 专用，不常用 |
| zoho-email-integration | ❌ 删除 | Zoho 专用，不常用 |
| email-daily-summary | ❌ 删除 | 特殊功能，可脚本替代 |

### 5. GitHub 相关（3个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| github (built-in) | ✅ 保留 | 内置技能 |
| github (workspace) | ❌ 删除 | 重复 |
| gimhub | ❌ 删除 | 命名不规范，功能重叠 |

### 6. Obsidian（2个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| obsidian (built-in) | ✅ 保留 | 内置技能 |
| obsidian (workspace) | ❌ 删除 | 重复 |

### 7. Home Assistant（2个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| homeassistant | ✅ 保留 | 主力技能 |
| home-assistant | ❌ 删除 | 重复（命名差异） |

### 8. Slack（2个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| slack (built-in) | ✅ 保留 | 内置技能 |
| slack (workspace) | ❌ 删除 | 重复 |

### 9. Discord（2个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| discord (built-in) | ✅ 保留 | 内置技能 |
| discord (workspace) | ❌ 删除 | 重复 |

### 10. Gog（2个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| gog (built-in) | ✅ 保留 | 内置技能 |
| gog (workspace) | ❌ 删除 | 重复 |

### 11. mcporter（2个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| mcporter (built-in) | ✅ 保留 | 内置技能 |
| mcporter (workspace) | ❌ 删除 | 重复 |

### 12. Paperless（2个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| paperless-ngx | ✅ 保留 | 主力技能（NGX 版本） |
| paperless | ❌ 删除 | 旧版本 |

### 13. Remotion 视频相关（3个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| remotion-video-toolkit | ✅ 保留 | 功能最完整 |
| remotion-best-practices | ❌ 删除 | 内容已包含 |
| remotion-server | ❌ 删除 | 服务端部分已整合 |

### 14. 搜索相关（6个重叠 → 建议2个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| ddg-search | ✅ 保留 | DuckDuckGo 搜索（主力） |
| serper | ✅ 保留 | Google 搜索（备选） |
| google-web-search | ❌ 删除 | 与 serper 重叠 |
| super-websearch-realtime | ❌ 删除 | 特殊版本 |
| firecrawl-search | ❌ 删除 | 特殊用途 |
| yutori-web-research | ❌ 删除 | 特殊用途 |

### 15. 前端/UI相关（10个重叠 → 建议2个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| frontend-design | ✅ 保留 | 通用前端设计 |
| human-optimized-frontend | ✅ 保留 | 人机优化专项 |
| pinak-frontend-guru | ❌ 删除 | 特殊版本 |
| ui-audit | ❌ 删除 | 功能重叠 |
| ui-skills | ❌ 删除 | 通用版 |
| ui-ux-pro-max | ❌ 删除 | 特殊版本 |
| web-design-guidelines | ❌ 删除 | 内容已包含 |
| web-perf | ❌ 删除 | 性能专项，可整合 |
| vercel-react-best-practices | ❌ 删除 | 特殊内容 |
| nextjs-expert | ❌ 删除 | 特殊框架 |

### 16. 记忆/上下文相关（6个重叠 → 建议1个）
| 技能名称 | 状态 | 建议 |
|----------|------|------|
| basal-ganglia-memory | ✅ 保留 | 主力记忆系统 |
| memory-pipeline | ❌ 删除 | 功能重叠 |
| memos | ❌ 删除 | 特殊用途 |
| memos-plugin | ❌ 删除 | 插件版本 |
| memU | ❌ 删除 | 特殊版本 |
| context-compressor | ❌ 删除 | 功能已整合 |
| context-recovery | ❌ 删除 | 功能已整合 |

### 17. 不常用/特殊用途技能（建议删除）
| 技能名称 | 原因 |
|----------|------|
| checkers-sixty60 | 南非超市专用 |
| diet-tracker | 个人减肥追踪 |
| seoul-subway | 韩国地铁 |
| swiss-transport | 瑞士交通 |
| uk-trains | 英国火车 |
| trimet | 美国波特兰交通 |
| stremio-cast | 视频流媒体 |
| roon-controller | 音乐播放器 |
| openpet | 虚拟宠物游戏 |
| spool | Threads 社交 |
| vocal-chat | 语音聊天 |
| wang1998sheng_bot | 个人定制 |
| xiaohongshu-mcp | 小红书 |
| youtube-voice-summarizer-elevenlabs | 特殊用途 |
| yt-video-downloader | YouTube下载 |
| use-soulseek | P2P音乐 |
| unifi | 网络设备 |
| zellij | 终端工具 |

---

## 精简统计

| 类别 | 原数量 | 保留数量 | 删除数量 |
|------|--------|----------|----------|
| LinkedIn | 6 | 1 | 5 |
| 浏览器 | 12 | 1 | 11 |
| n8n | 5 | 1 | 4 |
| 邮件 | 6 | 2 | 4 |
| GitHub | 3 | 1 | 2 |
| Obsidian | 2 | 1 | 1 |
| Home Assistant | 2 | 1 | 1 |
| Slack | 2 | 1 | 1 |
| Discord | 2 | 1 | 1 |
| Gog | 2 | 1 | 1 |
| mcporter | 2 | 1 | 1 |
| Paperless | 2 | 1 | 1 |
| Remotion | 3 | 1 | 2 |
| 搜索 | 6 | 2 | 4 |
| 前端/UI | 10 | 2 | 8 |
| 记忆 | 7 | 1 | 6 |
| 不常用 | 19 | 0 | 19 |
| **总计** | **93** | **18** | **75** |

---

## 保留的核心技能（按业务重要性）

### 航空业务相关
- linkedin（业务开发）
- gmail, imap-smtp-email（邮件沟通）
- himalaya（邮件 CLI，已配置）
- ddg-search, serper（搜索）
- browser-use（浏览器自动化）

### 系统维护相关
- basal-ganglia-memory（记忆系统）
- healthcheck（内置，健康检查）
- skill-creator（内置，技能创建）
- node-connect（内置，节点连接）

### 办公自动化
- n8n（工作流）
- paperless-ngx（文档管理）
- excel（表格处理）
- docx（文档处理）

### 其他保留
- homeassistant（智能家居）
- weather（天气）
- github（内置）
- obsidian（内置）
- slack（内置）
- discord（内置）
- clawhub（内置）

---

*生成时间：2026-03-31 00:xx*