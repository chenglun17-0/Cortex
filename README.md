# Cortex 智能研发项目管理系统

> 采用前后端分离架构，核心特色为 **"Web 管理端 + CLI 开发端"** 的双端协同研发管理系统。

## 📖 项目简介

Cortex 是一个专为研发团队设计的智能项目管理系统，将项目管理与开发工作流深度融合：

- **Web 前端**：提供敏捷看板与数据报表，用于项目进度的宏观监控
- **CLI 终端**：专为技术人员设计，实现"开发即管理"，将工单状态流转与 Git 操作原子化绑定，消除上下文切换
- **AI 能力**：基于 LangChain + RAG 的智能辅助功能（规划中）

## ✨ 核心特性

### 🔄 双端协同
- **Web 管理端**：可视化看板、任务管理、团队协作
- **CLI 开发端**：命令行操作任务、自动化 Git 工作流

### 🚀 开发工作流自动化
- `ctx tasks start <id>`：自动切换 Git 分支并更新任务状态
- `ctx tasks pr`：自动推送代码并创建 Pull Request
- `ctx tasks done`：自动合并代码、清理分支
- `ctx tasks list --json`：JSON 格式输出，便于 AI 解析

### 🤖 AI 智能辅助（MCP 集成）
- **MCP 服务器**：支持 Claude Desktop、Cline、Cursor 等 AI 工具
- **任务管理工具**：AI 可直接调用 Cortex CLI 进行任务操作
- **工单智能聚合**（规划中）：语义查重、解决方案推荐
- **代码智能辅助**（规划中）：自动生成 Commit Message 和 PR 描述、智能代码审查

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Git

### 快速启动

使用一键启动脚本：

```bash
# 启动前后端服务
./scripts/start-all.sh

# 停止前后端服务
./scripts/stop-all.sh

# 查看日志
tail -f logs/backend.log
tail -f logs/frontend.log
```

### 安装步骤

#### 1. 后端服务初始化

```bash
cd cortex-backend

# 创建虚拟环境（仅首次需要）
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等
```

后端服务将运行在 `http://localhost:8000`

#### 2. 前端服务初始化

```bash
cd cortex-frontend

# 安装依赖（仅首次需要）
npm install
```

前端服务将运行在 `http://localhost:5173`

#### 3. CLI 工具安装

```bash
cd cortex-backend

# 安装 CLI 工具
pip install -e .

# 验证安装
ctx --help

# 登录系统
ctx auth login
```

## 📋 使用指南

### Web 端操作

1. 访问 `http://localhost:5173` 打开 Web 界面
2. 使用账号密码登录系统
3. 创建项目和任务
4. 在看板中管理任务状态

### CLI 端操作

#### MCP 服务器集成（AI 工具）

Cortex 支持 MCP (Model Context Protocol)，允许 AI 工具（如 Claude Desktop）直接调用 Cortex CLI。

```bash
# MCP 服务器已随 CLI 一起安装
cortex-mcp --help

# 配置 Claude Desktop（示例）
# 编辑 ~/Library/Application Support/Claude/claude_desktop_config.json
# 添加以下配置：
# {
#   "mcpServers": {
#     "cortex": {
#       "command": "python",
#       "args": ["-m", "cortex_mcp.server"],
#       "env": {"PYTHONPATH": "/path/to/cortex-backend"}
#     }
#   }
# }
```

详见 [MCP 集成指南](./docs/mcp-integration.md)

#### 认证管理

```bash
# 登录
ctx auth login

# 登出
ctx auth logout
```

#### 任务管理

```bash
# 查看分配给我的任务
ctx tasks list

# 开始任务 (自动创建分支并切换)
ctx tasks start <task_id>

# 提交代码并创建 PR
ctx tasks pr

# 完成任务 (合并后清理分支)
ctx tasks done
```

#### 配置管理

```bash
# 查看所有配置
ctx config list

# 设置配置项
ctx config set <key> <value>
```

### 开发工作流示例

```bash
# 1. 查看待办任务
ctx tasks list

# 2. 开始任务 #42
ctx tasks start 42
# → 自动创建并切换到 feat/task-42 分支
# → 任务状态更新为 IN_PROGRESS

# 3. 进行开发工作
# ... 编写代码 ...

# 4. 提交代码并创建 PR
ctx tasks pr
# → 自动 push 代码到远程
# → 任务状态更新为 REVIEW
# → 打开 PR 创建链接

# 5. PR 合并后完成任务
ctx tasks done
# → 切换回主分支并拉取最新代码
# → 任务状态更新为 DONE
# → 清理本地功能分支
```

## 📊 项目进度

### ✅ 已完成功能

#### 后端
- ✅ FastAPI 框架集成与基础架构
- ✅ Tortoise ORM 数据库集成
- ✅ JWT 认证系统
- ✅ 用户管理 (注册、登录、认证)
- ✅ 组织管理 (CRUD)
- ✅ 项目管理 (创建、查询、成员关联)
- ✅ 任务管理 (CRUD、状态管理、分支关联)
- ✅ 统一 API 路由系统

#### CLI
- ✅ 用户认证 (login/logout)
- ✅ 任务列表查看
- ✅ 任务启动 (自动分支管理)
- ✅ PR 创建流程
- ✅ 任务完成 (分支清理)
- ✅ 配置管理
- ✅ JSON 输出支持

#### MCP 服务器
- ✅ MCP 协议支持
- ✅ 5 个核心工具封装 (list_tasks, start_task, submit_pr, complete_task, get_task_status)
- ✅ 结构化错误处理
- ✅ Claude Desktop 集成文档

#### 前端
- ✅ 用户登录页面
- ✅ 项目列表展示
- ✅ 基础路由配置
- ✅ React Query 状态管理集成

### 🚧 开发中功能

- 🚧 任务看板拖拽功能
- 🚧 项目详情与成员管理
- 🚧 任务详情与评论功能
- 🚧 数据统计与报表

### 📝 规划中功能

- 📝 AI 工单智能聚合 (语义查重、解决方案推荐)
- 📝 AI 代码智能辅助 (自动生成文档、智能审查)
- 📝 向量数据库集成 (pgvector)
- 📝 Git 平台集成 (GitHub/GitLab)
- 📝 通知系统
- 📝 团队协作功能增强

## 🤝 开发规范

本项目采用 **LeanSpec** 轻量级规范方法进行开发管理：

- 所有重要功能开发前需先创建规范文档 (`specs/`)
- 使用 `lean-spec` CLI 工具管理规范状态
- 详见 [AGENTS.md](./AGENTS.md) 了解完整的开发协作指南

## 📚 文档

- [AGENTS.md](./AGENTS.md) - AI 代理协作指南与开发规范
- [docs/project.md](./docs/project.md) - 项目详细说明与技术选型
- [docs/implementation.md](./docs/implementation.md) - 实现细节与目录结构说明
- [docs/mcp-integration.md](./docs/mcp-integration.md) - MCP 服务器集成指南
- [openspec/changes/add-mcp-server/](./openspec/changes/add-mcp-server/) - MCP 功能规格文档

## 🔒 安全注意事项

- 请勿将 `.env` 文件提交到版本控制
- JWT Token 请妥善保管
- 生产环境请使用强密码和 HTTPS
- 定期更新依赖包以修复安全漏洞

## 📄 License

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

**Cortex** - 让研发管理回归代码本身
