# SIGS Design Agent Game Demo

AR 校园探索与共创平台 —— 清华大学深圳国际研究生院

## 环境要求

| 工具 | 安装方式 |
|------|---------|
| Python >= 3.11 | https://www.python.org/downloads/ |
| uv | `pip install uv` |
| Node.js | https://nodejs.org/ （需包含 npm） |

## 一键启动

Windows 双击或终端运行：

```
.\start.bat # 一键启动的终端指令，复制前面的到终端，回车启动整个前后端。
```

```
start.bat
```

脚本会自动完成：
1. 检测并释放端口占用（8888、3111）
2. 检查 uv 和 node 是否已安装
3. 首次运行自动安装依赖（`uv sync`、`npm install`）
4. 在两个新窗口启动后端和前端服务

启动后访问：

| 地址 | 说明 |
|------|------|
| http://localhost:3111 | 前端页面 |
| http://localhost:8888 | 后端 API |
| http://localhost:8888/docs | API 文档（Swagger） |

## 停止服务

双击或终端运行：

```
stop.bat
```

或直接关闭后端/前端对应的终端窗口。

## 手动启动

如果脚本有问题，可以分别手动启动：

```bash
# 后端（在 backend/ 目录下）
cd backend
uv sync                  # 首次安装依赖
uv run uvicorn main:app --host 0.0.0.0 --port 8888 --reload

# 前端（在 frontend/ 目录下，新开一个终端）
cd frontend
npm install              # 首次安装依赖
npx live-server --port=3111 --open=/pages/landing.html
```
