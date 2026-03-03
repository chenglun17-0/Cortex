# 后端 API 模块（`cortex-backend/app`）

## 1. 模块结构

| 子模块 | 目录 | 职责 |
|--------|------|------|
| API 接入层 | `api/` | 路由聚合、端点实现、鉴权依赖 |
| 核心能力层 | `core/` | 配置、安全、上下文能力 |
| 数据模型层 | `models/` | Tortoise ORM 模型与关系 |
| 契约层 | `schemas/` | Pydantic 请求/响应模型 |
| 服务层 | `services/` | 可复用业务服务（向量检索） |

## 2. 关键入口

| 文件 | 说明 |
|------|------|
| `app/main.py` | FastAPI 初始化、`/api/v1` 路由挂载、ORM 注册 |
| `app/api/v1/api.py` | v1 路由聚合（organizations/users/login/tasks/projects/similarity） |
| `app/api/deps.py` | `get_current_user` 鉴权依赖 |

## 3. 路由模块清单

| 端点文件 | 主要能力 |
|----------|----------|
| `endpoints/login.py` | Token 登录签发 |
| `endpoints/users.py` | 用户注册、当前用户查询/更新、用户搜索 |
| `endpoints/organizations.py` | 组织创建与查询 |
| `endpoints/projects.py` | 项目 CRUD 与成员管理 |
| `endpoints/tasks.py` | 任务 CRUD、评论、访问控制、软删除 |
| `endpoints/similarity.py` | 相似任务检索与健康检查 |

## 4. 模型清单

| 模型 | 文件 | 说明 |
|------|------|------|
| `Organization` | `models/organization.py` | 组织主体 |
| `User` | `models/user.py` | 用户主体与认证信息 |
| `Project` | `models/project.py` | 项目主体 |
| `ProjectMember` | `models/project_member.py` | 项目成员关联 |
| `Task` | `models/task.py` | 任务主体（含软删除字段 `deleted_at`） |
| `TaskComment` | `models/task.py` | 任务评论实体 |

## 5. 主要调用链

```text
HTTP Request
  -> app/main.py (FastAPI)
  -> api/v1/api.py (router)
  -> endpoints/*.py (业务编排)
  -> models/*.py + services/*.py
  -> schemas/*.py (response)
```

## 6. 依赖与注意事项

| 项目 | 说明 |
|------|------|
| 数据库 | PostgreSQL（Tortoise ORM） |
| 向量检索 | `services/vector_store.py` 依赖 pgvector / embedding |
| 鉴权 | JWT + `get_current_user` |
| 环境配置 | `core/config.py` |

⚠️ 说明：`main.py` 当前 `generate_schemas=True`，适合开发环境，生产环境需谨慎评估。
