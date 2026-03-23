# WebTop 部署指南（Windows 环境）

## 方案选择

由于您的系统是 Windows 且未安装 Docker，提供两种方案：

---

## 方案 A：本地 Playwright 持久化浏览器（推荐，立即可用）

**优点：**
- ✅ 无需 Docker，直接在 Windows 运行
- ✅ Cookie/Session 持久化保存
- ✅ 与现有脚本完全兼容
- ✅ 可配置自动重连和监控

**部署步骤：**

### 1. 安装/更新 Playwright

```powershell
pip install playwright
playwright install chromium
```

### 2. 创建持久化浏览器配置

已创建脚本：`scripts/webtop_local.py`

### 3. 配置浏览器用户数据目录

浏览器数据将保存在：`C:\Users\Haide\AppData\Local\OpenClaw\BrowserData`

### 4. 启动持久化浏览器

```powershell
python scripts/webtop_local.py --start
```

### 5. 运行 LinkedIn/RFQ 脚本

脚本会自动连接到持久化浏览器实例。

---

## 方案 B：Docker Desktop + WebTop（完整方案）

**优点：**
- ✅ 完整的 WebTop 体验
- ✅ 更好的隔离性
- ✅ 支持 VNC 远程桌面

**安装步骤：**

### 1. 安装 Docker Desktop

1. 下载：https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
2. 运行安装程序
3. 启用 WSL2 后端
4. 重启电脑

### 2. 验证安装

```powershell
docker --version
docker-compose --version
```

### 3. 创建 WebTop 配置

配置文件位置：`scripts/webtop/docker-compose.yml`

### 4. 启动 WebTop

```powershell
cd scripts/webtop
docker-compose up -d
```

### 5. 访问远程桌面

浏览器打开：http://localhost:3000

---

## 推荐

**建议先使用方案 A（本地 Playwright）**，原因：
1. 立即可用，无需安装额外软件
2. 与现有工作流完全兼容
3. 性能更好（无容器开销）

如果后续需要云端部署或更强的反爬能力，再考虑方案 B。

---

## 下一步

我将为您部署方案 A（本地持久化浏览器方案），包括：
- [x] 创建持久化浏览器启动脚本
- [x] 配置浏览器用户数据目录
- [x] 添加 Watchdog 监控
- [x] 更新 LinkedIn 脚本连接配置

是否继续？
