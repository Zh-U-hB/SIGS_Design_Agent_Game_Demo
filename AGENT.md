# AGENT.md

> **版本**: 2.1.0
> **更新时间**: 2026-04-23
> **项目**: SIGS Design Agent Game Demo
>
> 本文件是给编程 AI Agent 的系统提示文档。所有参与代码开发的 AI Agent 必须先阅读本文件和 `开发规则.md`，严格遵守项目规范。

---

## 一、项目概述

**项目名称**: SIGS Design Agent Game Demo — 清华大学深圳国际研究生院 AR 校园探索共创平台

**技术栈**:
- 后端: Python + FastAPI + SQLAlchemy + asyncpg
- 前端: 原生 HTML/CSS/JavaScript
- 数据库: PostgreSQL（云端）
- 包管理: uv（Python）、npm（前端）
- 代码检查: Ruff

**项目目录结构**:
```
backend/     Python/FastAPI 后端代码
frontend/    原生 HTML/CSS/JS 前端代码
data/        数据相关文件（实际数据在云端数据库）
test/        测试脚本目录（与源码路径镜像）
temp/        临时文件、日志、缓存（gitignored）
doc/         项目设计文档（按分类存放）
demo_doc/    Demo 参考文档和 HTML 原型
dev_doc/     开发过程中的临时文档（PR review、临时笔记）
.env.example 环境变量配置模板
```

---

## 二、必须遵守的开发规则

### 2.1 优先级规则

当多个文档存在冲突时，按以下优先级执行：

1. **`开发规则.md`** — 最高优先级，权威规则
2. **本文文件 (`AGENT.md`)** — Agent 开发规范
3. **`CLAUDE.md`** — Claude Code 特定规范
4. **其他文档** — 设计文档、技术方案等

### 2.2 核心开发规则摘要

| 规则类别 | 要求 |
|----------|------|
| **函数长度** | ≤ 200 行 |
| **文件长度** | ≤ 800 行 |
| **异常处理** | 不允许裸 `except`，必须指定异常类型 |
| **SQL 安全** | 仅使用参数化查询，禁止字符串拼接 |
| **敏感信息** | 仅通过环境变量注入，禁止硬编码或记录到日志 |
| **测试覆盖** | 一个源码文件对应一个测试文件，测试通过才算完成 |
| **代码检查** | 必须通过 `ruff check .` 检查后再提交 |

### 2.3 命名规范

| 范围 | 风格 | 示例 |
|------|------|------|
| Python 文件、变量、函数 | snake_case | `user_service.py`, `get_user_by_id` |
| Python 类名 | PascalCase | `UserService` |
| Python 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| HTML/CSS/JS 文件、CSS 类名 | kebab-case | `game-board.html`, `.game-container` |
| JS 变量/函数 | camelCase | `getUserData` |
| JS 常量 | UPPER_SNAKE_CASE | `API_BASE_URL` |
| API 路径 | kebab-case 小写复数 | `/api/v1/users`, `/api/v1/designs` |

---

## 三、Git 规范

### 3.1 分支策略

- `main`: 开发分支，日常开发在此分支
- `serve`: 稳定分支，测试通过后合并，用于部署
- `feature/xxx`: 功能分支（可选），大型功能从 main 拉取

### 3.2 Commit 格式

```
<类型>: <简述>
```

类型: `feat`, `fix`, `refactor`, `test`, `docs`, `style`, `chore`

示例: `feat: 添加用户注册接口`

### 3.3 合并规则

- 功能开发完成需通过测试才能合并
- 合并到 `serve` 前需确认所有测试通过
- 禁止 `--force` 推送到 `serve`

---

## 四、API 接口规范

### 4.1 基本规则

- 风格: RESTful
- 数据格式: JSON
- 路径前缀: `/api/v1/`
- 资源名使用复数名词

### 4.2 HTTP 方法语义

| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 获取资源 | `GET /api/v1/designs` |
| POST | 创建资源 | `POST /api/v1/designs` |
| PUT | 全量更新 | `PUT /api/v1/designs/{id}` |
| PATCH | 部分更新 | `PATCH /api/v1/designs/{id}` |
| DELETE | 删除资源 | `DELETE /api/v1/designs/{id}` |

### 4.3 认证方式

使用 API Key 认证，通过请求头传递:
```
X-API-Key: <your-api-key>
```

### 4.4 统一响应格式

成功响应:
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

错误响应:
```json
{
  "code": 40001,
  "message": "错误描述",
  "data": null
}
```

常用错误码:
- `0`: 成功
- `40001`: 参数错误
- `40101`: API Key 缺失或无效
- `40401`: 资源不存在
- `50001`: 服务器内部错误

---

## 五、测试规范

### 5.1 测试文件路径规则

测试脚本路径与源码路径镜像（一对一）:

| 源码文件 | 测试文件 |
|----------|----------|
| `backend/database/serve.py` | `test/backend/database/test_serve.py` |
| `backend/api/design.py` | `test/backend/api/test_design.py` |
| `backend/services/session_service.py` | `test/backend/services/test_session_service.py` |

### 5.2 测试框架

- 使用 pytest
- 异步测试使用 pytest-asyncio
- HTTP 客户端使用 httpx

---

## 六、文档管理规范 ⚠️

### 6.1 文档存放规则

**重要**: 当被要求"写一个文档"或"生成报告"时，必须先读取 `doc/00_文档存放规则.md`。

#### 文档分类结构

```
doc/
├── 00_文档存放规则.md          # 存放规则定义（AI 写文档前必读）
├── INDEX.md                     # 主索引 — 所有文档导航
│
├── 01_architecture/             # 架构设计 — 技术架构、框架、数据库
├── 02_product/                  # 产品设计 — 交互设计、功能需求
├── 03_reports/                  # 报告文档 — 代码报告、审计报告
├── 04_plans/                    # 计划文档 — 工作计划、路线图
├── 05_meetings/                 # 会议记录 — 会议纪要、决策记录
├── 06_references/               # 参考资料 — 外部文档、研究资料
└── archive/                     # 归档区 — 过期/废弃文档
```

#### AI 写文档时的操作流程

1. **Step 1**: 读取 `doc/00_文档存放规则.md`
2. **Step 2**: 根据用户描述判断文档类型
3. **Step 3**: 按命名格式 `[描述]_[YYYY-MM-DD].md` 确定文件名
4. **Step 4**: 写入文档内容（包含标准头部元数据）
5. **Step 5**: 更新 `doc/INDEX.md` 添加新文档链接

#### 文档类型判断

| 用户请求关键词 | 存放目录 |
|----------------|----------|
| "代码报告"、"审计"、"review"、"安全分析" | `doc/03_reports/` |
| "工作计划"、"todo"、"后续工作"、"待办" | `doc/04_plans/` |
| "架构设计"、"技术方案"、"系统设计" | `doc/01_architecture/` |
| "交互设计"、"用户体验"、"产品需求" | `doc/02_product/` |
| "会议纪要"、"决策记录" | `doc/05_meetings/` |

#### 文件命名规则

- 标准格式: `[描述]_[YYYY-MM-DD].md`
- 报告/计划类文档**必须包含日期**
- 架构/设计类文档通常不需要日期

#### 文档头部元数据

每个文档应包含标准头部:

```markdown
# 文档标题

> **版本**: X.Y.Z
> **更新日期**: YYYY-MM-DD
> **文档编辑**: 作者名
> **状态**: [草案/评审中/已发布/已归档]
> **关联文档**: [相关文档](路径)
```

### 6.2 代码中的文档注释

- Python: 使用 docstring 描述函数/类的功能
- JavaScript: 使用 JSDoc 风格注释
- 复杂逻辑必须添加注释说明

---

## 七、环境配置规范

### 7.1 环境变量管理

- 所有环境变量模板记录在 `.env.example` 中（不含真实值）
- 新增环境变量时必须同步更新 `.env.example`
- `.env` 文件在 `.gitignore` 中，禁止提交
- 敏感信息（数据库密码、API Key）仅通过环境变量注入

### 7.2 必要的环境变量

```bash
# 数据库配置
DATABASE_URL=
DATABASE_NAME=

# API 配置
API_KEY=
API_HOST=
API_PORT=

# 前端配置
FRONTEND_URL=
```

---

## 八、安全规范

| 规则 | 说明 |
|------|------|
| **输入校验** | 所有外部输入必须校验 |
| **SQL 安全** | 仅使用参数化查询，禁止拼接字符串 |
| **敏感信息** | 禁止在日志中输出 API Key、密码等 |
| **HTTPS** | 生产环境必须启用 HTTPS |
| **错误信息** | 错误响应不得泄露内部实现细节 |

---

## 九、常用命令

```bash
# 后端 — 创建虚拟环境并安装依赖（首次）
cd backend && uv sync

# 后端 — 运行开发服务器
cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 代码检查
ruff check .

# 代码自动修复
ruff check --fix .

# 代码格式化
ruff format .

# 运行测试
pytest
```

---

## 十、Agent 开发检查清单

在完成任务前，确认以下检查项:

- [ ] 代码符合命名规范
- [ ] 函数长度 ≤ 200 行，文件长度 ≤ 800 行
- [ ] 无裸 `except`，所有异常都有明确类型
- [ ] SQL 使用参数化查询
- [ ] 敏感信息通过环境变量注入，无硬编码
- [ ] 创建了对应的测试文件
- [ ] 通过 `ruff check .` 检查
- [ ] 如涉及文档，已按 `doc/00_文档存放规则.md` 存放
- [ ] Commit 信息格式正确: `<类型>: <简述>`

---

## 十一、问题排查

### 11.1 常见问题

| 问题 | 解决方案 |
|------|----------|
| 导入模块失败 | 检查是否在 `backend/` 目录下运行，是否执行了 `uv sync` |
| 数据库连接失败 | 检查 `.env` 中的 `DATABASE_URL` 是否正确 |
| Ruff 检查失败 | 运行 `ruff check --fix .` 自动修复，或手动修复剩余问题 |
| 测试失败 | 检查测试文件路径是否与源码镜像，是否导入正确的模块 |

### 11.2 获取帮助

- 查阅 `开发规则.md` — 权威规则文档
- 查阅 `doc/INDEX.md` — 文档索引
- 查阅 `doc/00_文档存放规则.md` — 文档存放规则

---

> **最后更新**: 2026-04-23
> **维护者**: 项目组
>
> 如果你在开发过程中发现本文件需要更新，请及时维护。
