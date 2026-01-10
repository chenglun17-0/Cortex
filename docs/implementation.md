# Implementation Details

本文档旨在说明 Cortex 智能研发项目管理系统的项目目录结构、技术实现方案及其核心组件。

## 1. 项目概览

Cortex 采用前后端分离的架构，并集成了专为开发者设计的 CLI 工具。项目结构如下：

- **cortex-backend**: 基于 FastAPI 的后端 API 服务，包含核心业务逻辑与 CLI 工具源码。
- **cortex-frontend**: 基于 React + Ant Design 的 Web 管理后台。
- **docs**: 项目文档与实现说明。

---

## 2. 目录结构

### 2.1 后端与 CLI (cortex-backend)
```text
cortex-backend/
├── app/                  # FastAPI 核心应用
│   ├── api/              # API 路由 (v1 分层)
│   │   └── v1/           # 业务接口 (用户、任务、组织等)
│   ├── core/             # 核心配置 (安全、环境变量、上下文)
│   ├── models/           # Tortoise ORM 数据库模型
│   └── schemas/          # Pydantic 数据验证模型
├── cli/                  # Cortex CLI 工具源码
│   ├── commands/         # CLI 命令实现 (auth, tasks, config)
│   ├── api.py            # CLI 与后端 API 交互封装
│   └── git.py            # Git 操作封装 (分支切换、推代码)
└── pyproject.toml        # 后端与 CLI 依赖配置
```

### 2.2 前端 (cortex-frontend)
```text
cortex-frontend/
├── src/
│   ├── features/         # 按功能模块组织的代码
│   │   ├── auth/         # 登录与权限
│   │   ├── projects/     # 项目管理
│   │   └── tasks/        # 任务看板与列表
│   ├── lib/              # 基础库配置 (axios, react-query)
│   ├── types/            # 全局 TypeScript 类型定义
│   └── App.tsx           # 根组件与路由配置
└── package.json          # 前端依赖配置
```

---

## 3. 技术实现

### 3.1 后端实现 (Backend)
- **Web 框架**: [FastAPI](https://fastapi.tiangolo.com/) - 利用异步特性处理高并发请求。
- **ORM**: [Tortoise ORM](https://tortoise.github.io/) - 异步 ORM，支持模型定义与自动迁移。
- **认证**: 基于 JWT (JSON Web Token) 的 OAuth2 密码流，确保前后端及 CLI 的通信安全。
- **数据流**: 遵循 `Schema -> Router -> Model` 的经典流转模式，确保数据验证与业务逻辑分离。

### 3.2 前端实现 (Frontend)
- **UI 框架**: React 19 + [Ant Design 6](https://ant.design/)。
- **状态管理 & 数据请求**: [React Query (TanStack Query)](https://tanstack.com/query/latest) - 负责服务端状态同步、缓存与 Loading 状态维护。
- **工程化**: 使用 Vite 作为构建工具，采用 TypeScript 进行全量类型约束。
- **模块化**: 采用 `features/` 目录组织代码，每个 feature 包含自己的页面组件与服务逻辑，提升可维护性。

### 3.3 CLI 实现 (CLI)
- **基础框架**: [Typer](https://typer.tiangolo.com/) - 提供美观且类型安全的命令行交互。
- **Git 协同**: 通过底层 Shell 调用或库操作，实现 `start` (自动切分支) 和 `done` (自动拉取合并) 等工作流。
- **配置管理**: 本地存储用户凭证与偏好设置，实现“一次登录，持续使用”。

---

## 4. 核心工作流

1. **开发者任务启动**:
   - 开发者在 CLI 执行 `ctx tasks start <id>`。
   - CLI 请求后端更新任务状态，并自动在本地创建对应的 Git 功能分支。
2. **任务提交与评审**:
   - 开发者执行 `ctx tasks pr`。
   - CLI 自动推送代码并触发 PR 创建流程（未来将集成 AI 生成描述）。
3. **Web 端监控**:
   - 项目经理通过 Web 前端查看看板，实时监控各任务的分支状态与进度。
