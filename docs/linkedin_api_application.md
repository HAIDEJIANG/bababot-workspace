# LinkedIn API 申请指南

## 📋 申请步骤

### 1️⃣ 访问 LinkedIn Developer Portal
网址：https://www.linkedin.com/developers/

### 2️⃣ 创建开发者账号
- 使用您的 LinkedIn 账号登录
- 点击 "Create app" 创建应用
- 填写应用信息：
  - **App Name**: AeroEdge Global - Aviation Data Collection
  - **Company**: AeroEdge Global Services Co., Ltd
  - **App Logo**: 公司 Logo（可选）
  - **Privacy Policy URL**: 公司网站（如有）
  - **User Agreement**: 公司网站（如有）

### 3️⃣ 选择 API 权限
根据我们的需求，申请以下权限：

| API | 用途 | 所需权限 |
|-----|------|---------|
| **Sign In with LinkedIn** | 用户认证 | `r_liteprofile`, `r_emailaddress` |
| **Profile API** | 获取用户资料 | `r_fullprofile` |
| **Share API** | 发布/读取帖子 | `w_member_social`, `r_basicprofile` |
| **Organization API** | 公司页面数据 | `r_organization_social` |
| **Advertising API** | 广告数据（可选） | `r_ads`, `r_ads_reporting` |

### 4️⃣ 提交审核
- LinkedIn 会审核您的应用
- 审核时间：通常 3-5 个工作日
- 可能需要提供：
  - 应用使用场景说明
  - 数据使用说明
  - 隐私保护措施

---

## 🔑 获取 API 凭证

审核通过后，您将获得：

```
Client ID:     xxxxxxxxxxxxxx
Client Secret: xxxxxxxxxxxxxx
Access Token:  xxxxxxxxxxxxxx (有效期 60 天)
```

---

## 💻 集成到采集脚本

获得 API 凭证后，我将帮您：

1. **配置认证**
   - 保存凭证到 `.env` 文件
   - 实现 OAuth 2.0 认证流程
   - 自动刷新 Access Token

2. **开发 API 采集脚本**
   - 获取 Feed 帖子
   - 获取公司页面更新
   - 获取群组讨论

3. **数据格式优化**
   - 结构化存储
   - 自动去重
   - 航材关键词过滤

---

## ⚠️ API 限制

| 限制类型 | 额度 |
|---------|------|
| **调用频率** | 500 次/天 (标准版) |
| **Rate Limit** | 100 次/小时 |
| **数据范围** | 仅公开帖子 + 已授权内容 |

---

## 📝 申请模板（英文）

**Application Description:**
```
AeroEdge Global is an aviation parts trading company specializing in 
aircraft engines, landing gear, and MRO services. We use LinkedIn data 
to:
1. Monitor industry trends and market intelligence
2. Track aviation parts trading opportunities
3. Connect with potential suppliers and customers
4. Analyze competitor activities

Data collected will be used internally for business intelligence only.
We respect user privacy and comply with LinkedIn's terms of service.
```

**Use Case:**
```
- Collect public posts related to aviation parts trading
- Monitor industry news and market updates
- Identify potential business opportunities
- Track competitor activities and market trends
```

---

## 🎯 替代方案（如果 API 申请被拒）

1. **Browser Relay 扩展** - 修复扩展连接问题
2. **人工采集 + 自动化处理** - 手动截图/复制，自动分析
3. **第三方数据服务** - 购买航空行业数据

---

**下一步：**
1. 访问 https://www.linkedin.com/developers/
2. 创建应用并提交审核
3. 获得 API 凭证后告诉我
4. 我帮您集成到采集系统

**预计时间：** 3-5 个工作日（审核时间）
