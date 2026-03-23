# OpenClaw 进阶配置教程知识点总结 (2026-03-16)
**来源**: 微信公众号文章《OpenClaw 进阶配置完全教程(2026)》
**整理时间**: 2026-03-16 14:35 (Asia/Hong_Kong)

---

## 一,AGENTS.md 配置要点

### 1.1 文件定位
- **位置**: workspace 根目录(与 SOUL.md 同级)
- **作用**: AI 的工作手册/行为宪法
- **加载时机**: 每次新 session 自动加载

### 1.2 与 SOUL.md/USER.md 的区别
SOUL.md, 作用=性格定义, 类比="你是一个随和,实在的助手"
USER.md, 作用=用户信息, 类比="你在帮谁"
AGENTS.md, 作用=工作手册, 类比="每天上班先看邮件,写完代码要测试,删文件前要问我"

### 1.3 Session 启动流程(必须包含)
```markdown

## Every Session
Before doing anything else:
1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. If in MAIN SESSION (direct chat with your human): Also read `MEMORY.md`
```

### 1.4 Session 类型说明
主 session, 说明=直接跟 AI 聊天的对话, MEMORY.md 读取= 读取
群聊 session, 说明=Discord 服务器里的群聊, MEMORY.md 读取= 不读取(安全)
子 agent session, 说明=AI 派出去执行任务的子进程, MEMORY.md 读取= 不读取
cron session, 说明=定时任务触发的对话, MEMORY.md 读取= 不读取

## 二,记忆系统实战配置

### 2.1 记忆分层结构
索引层, 文件=`MEMORY.md`, 用途=关于用户,能力概览,记忆索引, 大小建议=<40 行
项目层, 文件=`memory/projects.md`, 用途=各项目当前状态与待办, 大小建议=-
基础设施层, 文件=`memory/infra.md`, 用途=服务器,API,部署等配置速查, 大小建议=-
教训层, 文件=`memory/lessons.md`, 用途=踩过的坑,按严重程度分级, 大小建议=-
日志层, 文件=`memory/YYYY-MM-DD.md`, 用途=每日原始记录, 大小建议=-

### 2.2 写入规则
- **日志**: 写入 `memory/YYYY-MM-DD.md`, **项目状态**: 项目有进展时同步更新 `memory/projects.md`, **教训**: 踩坑后写入 `memory/lessons.md`, **MEMORY.md**: 只在索引变化时更新,保持精简

### [PROJECT:名称] 标题
- **结论**: 一句话总结, **文件变更**: 涉及的文件, **教训**: 踩坑点(如有), **标签**: #tag1 #tag2

### 2.4 铁律
- 记结论不记过程
- 标签便于 memorySearch 检索
- "Mental notes" don't survive session restarts. Files do.

### 2.5 好日志 vs 烂日志对比
**烂日志**(浪费 token,检索精度差):

### 部署
今天部署了项目.先试了直接跑,报错了.然后查了半天,发现是端口被占了......(三页流水账)

 **好日志**(精简,memorySearch 高命中率):

### [PROJECT:MyApp] 部署完成
- **结论**: 用 nginx 反代部署成功,监听 80 端口
- **文件变更**: `/etc/nginx/sites-available/myapp`
- **教训**: 直接暴露端口不可行,必须走 nginx 反代
- **标签**: #myapp #deploy #nginx

### 2.6 memoryFlush 配置(防止 AI 失忆)
在 `openclaw.json` 中配置:
```json
{
 "memory": {
 "flushIntervalMinutes": 30,
 "autoCompress": true,
 "embeddingModel": "siliconflow/bge-m3"
 }

## 三,子 Agent 并行任务

### 3.1 使用场景
- 2+ 独立任务可以并行处理, 任务之间无共享状态或顺序依赖, 需要同时处理多个独立查询

### 3.2 调用方法
```javascript
sessions_spawn({
 runtime: "subagent",
 task: "具体任务描述",
 mode: "run" // 或 "session"
})

### 3.3 效果对比
- 主脑单线程干活: 一个人变一支团队,并行派活

## 四,Cron 定时任务配置

### 4.1 使用场景
- 精确 timing matters("每周一上午 9 点整")
- 任务需要与主 session 历史隔离
- 想要不同的 model 或 thinking level
- 一次性提醒("20 分钟后提醒我")
- 输出直接发送到频道,无需主 session 参与

### 4.2 与 Heartbeat 的区别
多个检查可批量处理, Heartbeat=, Cron=
需要最近消息的对话上下文, Heartbeat=, Cron=
timing 可略有漂移(~30 分钟), Heartbeat=, Cron=
想通过合并定期检查减少 API 调用, Heartbeat=, Cron=
精确 timing, Heartbeat=, Cron=
任务隔离, Heartbeat=, Cron=
不同 model/thinking level, Heartbeat=, Cron=

### 4.3 配置示例
"cron": {
 "tasks": [
 "name": "daily-news",
 "schedule": "0 8 * * *",
 "task": "生成每日新闻摘要",
 "channel": "telegram"
 ]

## 五,Skill 开发入门

### 5.1 Skill 目录结构
skills/
└── my-skill/
 ├── SKILL.md # 技能描述和触发条件
 ├── index.js # 主入口
 ├── scripts/ # 脚本文件
 └── references/ # 参考资料

# 技能名称

## 描述
简短描述技能用途

## 触发条件
- 当用户说...
- 当需要...

## 使用方法
具体使用指令

### 5.3 开发流程
1. 创建 skill 目录
2. 编写 SKILL.md 定义触发条件
3. 实现核心逻辑(index.js 或 scripts/)
4. 测试技能触发
5. 更新文档

## 六,多渠道接入配置

### 6.1 Discord 接入
**关键配置**:
- 需要开启 MESSAGE CONTENT INTENT
- 在 Discord Developer Portal 中启用 Privileged Gateway Intents

### 6.2 Telegram Bot 配置
1. 通过 BotFather 创建 bot
2. 获取 bot token
3. 配置到 openclaw.json

### 6.3 多平台同时在线
- 消息路由自动处理
- 不同渠道使用不同格式化规则

## 七,openclaw.json 配置速查表

### 7.1 核心参数优化
},
 "enabled": true,
 "tasks": []
 "channels": {
 "telegram": {
 "botToken": "${TELEGRAM_BOT_TOKEN}"
 "discord": {
 "enabled": false,
 "botToken": "${DISCORD_BOT_TOKEN}",
 "messageContentIntent": true

## 八,调教前后效果对比
行为规范, 基础水平=SOUL.md 写了几行, 本篇调教后=完整行为宪法,知道什么该做什么不该做
记忆, 基础水平=有分层结构, 本篇调教后=自动维护,自动压缩,语义检索秒回
任务能力, 基础水平=主脑单线程干活, 本篇调教后=一个人变一支团队,并行派活
自动化, 基础水平=心跳能巡检, 本篇调教后=精确定时任务,早报晚报自动发
扩展性, 基础水平=装了几个 skill, 本篇调教后=自己能写 skill,想要什么能力就加什么
渠道, 基础水平=接了一个平台, 本篇调教后=多平台同时在线,消息路由自如
配置, 基础水平=能跑就行, 本篇调教后=每个参数都调到最优

## 待执行事项

### 已检查
- AGENTS.md 已包含核心配置(会话启动流程,记忆分层,安全边界), memory 目录存在,有日常志文件, ️ 缺少 `memory/projects.md`(项目层), ️ 缺少 `memory/infra.md`(基础设施层), ️ 缺少 `memory/lessons.md`(教训层)

### 待创建
1. 创建 `memory/projects.md` - 项目状态追踪
2. 创建 `memory/infra.md` - 基础设施配置速查
3. 创建 `memory/lessons.md` - 教训记录

*整理完成时间:2026-03-16 14:35 (Asia/Hong_Kong)*