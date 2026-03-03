# 仓库模块总览

## 1. 顶层目录职责

| 目录 | 职责 | 关键入口 |
|------|------|----------|
| `cortex-backend/` | 后端 API 与 CLI 代码 | `app/main.py`、`cli/main.py` |
| `cortex-frontend/` | Web 前端管理端 | `src/main.tsx`、`src/App.tsx` |
| `scripts/` | 本地运行与部署脚本 | `start-all.sh`、`stop-all.sh` |
| `docs/` | 项目文档、规则与模块说明 | `project.md`、`rules/`、`modules/` |
| `openspec/` | 规格变更与提案管理 | `project.md`、`changes/`、`specs/` |
| `specs/` | 旧版规格/任务文档 | `SPEC.md` 系列 |

## 2. 模块依赖关系

| 上游 | 下游 | 说明 |
|------|------|------|
| 前端 (`cortex-frontend`) | 后端 API (`cortex-backend/app`) | 通过 `/api/v1/*` HTTP 接口交互 |
| CLI (`cortex-backend/cli`) | 后端 API (`cortex-backend/app`) | `ctx` 命令驱动任务状态流转 |
| 后端 API (`cortex-backend/app`) | 数据库与向量检索模块 | ORM 持久化 + 相似任务检索 |
| CLI (`cortex-backend/cli`) | Git Provider | 调用 GitHub/GitLab/Gitee 相关能力 |
| 后端 API | PostgreSQL / pgvector | 存储业务数据与向量检索数据 |
| `scripts/` | 前后端模块 | 启动、停止、日志运维 |

## 3. 关键应用入口

| 模块 | 入口文件 | 说明 |
|------|----------|------|
| 后端 API | `cortex-backend/app/main.py` | FastAPI 应用与路由挂载 |
| CLI | `cortex-backend/cli/main.py` | Typer 命令入口（`ctx`） |
| 前端 | `cortex-frontend/src/main.tsx` | React 根挂载与 QueryClient 注入 |
| 前端路由 | `cortex-frontend/src/App.tsx` | 页面路由与登录守卫 |
| 本地运行脚本 | `scripts/start-all.sh` / `scripts/stop-all.sh` | 一键启停本地环境 |

## 4. 推荐阅读顺序

1. `backend-app.md`
2. `database-vector.md`
3. `backend-cli.md`
4. `frontend-web.md`
5. `runtime-and-tooling.md`
