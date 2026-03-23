# 浏览器自动化工具使用原则
**来源**: 微信公众号「科技充电站」-《Playwright MCP 和 Chrome DevTools MCP,用了半年后我终于明白,原来 90% 的人都用错了!》
**学习时间**: 2026-03-05 16:37

---

## 核心设计哲学对比

### Playwright MCP — 「像用户一样看页面」
- 提供**可访问性树(Accessibility Tree)**而非原始 HTML
- 过滤掉 `<div class="css-1a2b3c">`,`data-analytics-id="xxx"` 等噪声
- 只保留 AI 真正需要的语义信息:「这是个按钮,叫提交,可以点击」

**优势**:
1. Token 消耗暴降 70-80%(同一页面:原始 DOM 5-10 万 Token → 可访问性树 2-5 千 Token)
2. 信噪比高,AI 推理准确率提升
3. **Auto-wait 机制** — 操作前自动确认元素已加载,可见,位置稳定,没被弹窗挡住

### Chrome DevTools MCP — 「像开发者一样看页面」
- 直接封装 Chrome DevTools Protocol
- 开放浏览器内部运行时状态:网络请求瀑布图,JS 调用栈,计算样式,性能轨迹
- 信息极其丰富,但可能撑爆上下文窗口

## 核心差异速查表
感知方式, Playwright MCP=可访问性树(语义化,低噪声), DevTools MCP=DOM 树/源码(全量信息,高噪声)
Token 消耗, Playwright MCP=低(2k-5k), DevTools MCP=高(50k-100k)
等待机制, Playwright MCP=原生 Auto-wait,操作自动等元素就绪, DevTools MCP=需要 AI 显式等待或轮询
选择器, Playwright MCP=基于角色和文本(语义稳定), DevTools MCP=基于 CSS/XPath(容易因重构失效)
调试能力, Playwright MCP=基础(Console 文本日志), DevTools MCP=深度(对象审查,堆栈追踪,网络全链路)
性能分析, Playwright MCP=无, DevTools MCP=Performance Trace + Lighthouse
环境模拟, Playwright MCP=无, DevTools MCP=暗色模式,网络限速,CPU 节流,地理位置
工具数量, Playwright MCP=~21 个(精简), DevTools MCP=26+ 个(全面但认知负荷高)

## 实战原则

### Snapshot vs Screenshot
**原则**:
- **默认永远用 snapshot** — 检查文字,结构,表单,元素存在性
- **只有验证视觉效果时才用 screenshot** — 颜色,间距,图片渲染,Canvas/SVG

**原因**:
- Snapshot Token 消耗只有截图的 **1/10 到 1/50**
- AI 对结构化数据的理解准确率远高于截图

### 工具分工
> **Playwright 是默认选择,DevTools 是按需补充**

日常页面操作和 E2E 测试, 推荐工具=Playwright, 说明=导航,点击,填表,验证流程
性能排查和网络调试, 推荐工具=DevTools, 说明=「首页加载为什么要 5 秒?」类问题
CSS 排查和环境模拟, 推荐工具=DevTools, 说明=computed style,暗色模式,网络限速
复杂自动化脚本, 推荐工具=Playwright, 说明=跨页面,跨 iframe,文件上传下载

**95% 的场景 Playwright 就够了,剩下 5% 的疑难杂症才需要 DevTools**

## 对 OpenClaw Browser 的启示
1. **优先使用 snapshot 而非 screenshot** — 节省 Token,提高准确率
2. **利用 browser_snapshot 获取页面结构** — 基于 Accessibility Tree
3. **复杂调试时考虑 DevTools MCP 补充** — 性能分析,网络请求排查
4. **避免直接操作原始 DOM** — 使用语义化选择器(基于角色和文本)

*记录时间:2026-03-05 16:37 (Asia/Hong_Kong)*