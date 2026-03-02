# 数据库与向量检索模块规则

## 1. 模块职责

| 项 | 内容 |
|----|------|
| 模块范围 | `cortex-backend/migrations`、`app/models`、`app/services/vector_store.py` |
| 核心职责 | 维护 PostgreSQL 主数据与 pgvector 相似检索能力 |
| 边界说明 | 负责数据结构与检索能力，不负责 HTTP 接口编排 |

## 2. 子模块边界

| 子模块 | 目录/文件 | 职责 |
|--------|-----------|------|
| ORM 模型 | `app/models` | 定义业务表结构与关系 |
| 迁移管理 | `migrations/models`、Aerich 配置 | 维护结构演进 |
| 向量服务 | `app/services/vector_store.py` | 任务向量写入、检索、删除 |
| 迁移规范 | `docs/rules/database-migration-process.md` | 迁移故障处理与执行流程 |

## 3. 数据来源

| 数据 | 来源 |
|------|------|
| 业务表数据 | PostgreSQL 主库 |
| 向量索引数据 | PostgreSQL + pgvector 扩展 |
| 连接配置 | `DATABASE_URL` |

## 4. 关键机制

| 机制 | 说明 |
|------|------|
| 迁移机制 | `aerich migrate` + `aerich upgrade` |
| 版本记录机制 | `aerich` 表记录已应用迁移 |
| 向量检索机制 | 任务文本 embedding 存储与相似度查询 |

## 5. 依赖关系

| 依赖模块 | 关系 |
|----------|------|
| 后端 API 模块 | 提供任务写入与相似检索接口 |
| 运行部署模块 | 提供数据库服务与连接配置 |

## 6. 变更规则

1. 修改模型字段后必须立即执行迁移并验证。
2. 向量结构或索引策略调整时必须补充回归验证。
3. 数据库连接配置变更时必须同步检查本地与容器运行方式。

## 7. 严禁事项

- ⚠️ 严禁只生成 migration 不执行 upgrade。
- ⚠️ 严禁手工改表后不补 migration 版本记录。
- ⚠️ 严禁在文档或脚本中写入真实数据库密钥。
