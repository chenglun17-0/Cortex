# Cortex 模块规则总览

本文件用于维护 Cortex 项目的模块边界、依赖关系与规则文档索引。

## 1. 模块清单

| 模块 | 主责 | 协作模块 | 主要目录 | 详细规则 |
|------|------|----------|----------|----------|
| 后端 API | API 契约、鉴权、业务流程编排 | 数据库与向量检索、CLI、前端 | `cortex-backend/app` | `docs/rules/modules/backend-api.md` |
| CLI 工作流 | 任务流转与 Git/PR 自动化 | 后端 API、Git Provider | `cortex-backend/cli` | `docs/rules/modules/cli-workflow.md` |
| 前端 Web | 页面交互、请求编排、数据展示 | 后端 API | `cortex-frontend/src` | `docs/rules/modules/frontend-web.md` |
| 运行与部署 | 本地脚本、容器、发布流程 | 后端 API、前端、数据库 | `scripts`、`docker-compose.yml` | `docs/rules/modules/runtime-deploy.md` |
| 数据库与向量检索 | 模型落库、迁移、向量索引能力 | 后端 API | `cortex-backend/migrations`、`app/services` | `docs/rules/modules/database-vector.md` |

## 2. 模块依赖关系

| 上游模块 | 下游模块 | 依赖说明 |
|----------|----------|----------|
| 前端 Web | 后端 API | 通过 `/api/v1` 调用认证、项目、任务、相似检索接口 |
| CLI 工作流 | 后端 API | 调用任务与认证接口进行状态同步 |
| CLI 工作流 | Git 平台 Provider | 创建/检查/合并 PR 或 MR |
| 后端 API | 数据库与向量检索 | 主业务数据和相似检索均依赖 PostgreSQL |
| 运行与部署 | 全模块 | 本地脚本与 Docker 编排支撑整体运行 |

## 3. 变更维护规则

1. 修改任一模块核心逻辑时，必须同步更新对应模块规则文档。
2. 若模块边界变化（目录重构、职责调整），必须先更新本文件再提交代码。
3. 新增跨模块依赖时，必须在本文件补充依赖关系表。

## 4. 关联规范

- 业务配置规范：`docs/rules/业务规则配置规范.md`
- 数据库迁移规范：`docs/rules/database-migration-process.md`

## 5. 严禁事项

- ⚠️ 严禁在未更新规则文档的情况下直接调整模块边界。
- ⚠️ 严禁跨模块直接复制业务常量，必须维护单一事实来源（Single Source of Truth）。
- ⚠️ 严禁在文档中记录密钥、密码、Token 等敏感信息。
