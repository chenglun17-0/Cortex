# 代码模块文档

本文档目录用于描述 **代码实现视角** 的模块结构、职责边界与依赖关系。  
规则约束请继续参考 `docs/rules/` 下文档。

## 模块索引

| 模块 | 文档 | 说明 |
|------|------|------|
| 仓库总览 | `repository-map.md` | 顶层目录职责、模块依赖关系、关键入口 |
| 后端 API 应用 | `backend-app.md` | `cortex-backend/app` 分层、路由与模型结构 |
| 数据库与向量检索 | `database-vector.md` | ORM 配置、迁移机制、pgvector 相似检索链路 |
| CLI 应用 | `backend-cli.md` | `cortex-backend/cli` 命令编排、Git/Provider/AI 交互 |
| 前端 Web 应用 | `frontend-web.md` | `cortex-frontend/src` 分层、路由与数据流 |
| 运行与工具链 | `runtime-and-tooling.md` | `scripts/`、本地启动停止与常用命令 |

## 使用建议

1. 先看 `repository-map.md` 建立全局认知，再按模块阅读。
2. 设计或重构前，先确认对应模块文档与 `docs/rules/` 是否一致。
3. 代码改动涉及模块边界时，同步更新本目录与 `docs/rules/`。
