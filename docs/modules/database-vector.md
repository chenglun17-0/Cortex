# 数据库与向量检索模块（`cortex-backend/app/db.py` + `services/vector_store.py`）

## 1. 模块范围

| 子模块 | 目录/文件 | 职责 |
|--------|-----------|------|
| ORM 配置 | `app/db.py` | 读取数据库配置并构建 `TORTOISE_ORM` |
| 迁移配置 | `aerich.toml`、`[tool.aerich]` | 定义迁移目录与 ORM 入口 |
| 迁移文件 | `migrations/models/` | 数据表结构演进 |
| 向量检索服务 | `app/services/vector_store.py` | embedding 生成、向量入库、相似任务查询 |

## 2. 关键入口

| 入口 | 说明 |
|------|------|
| `app/db.py:get_db_config()` | 将 `DATABASE_URL` 解析为 Tortoise 连接配置 |
| `app/db.py:TORTOISE_ORM` | ORM 配置常量（被 Aerich 与应用启动复用） |
| `app/services/vector_store.py:init_pgvector()` | 初始化 `task_embeddings` 表与向量索引 |
| `app/services/vector_store.py:search_similar_tasks()` | 余弦距离检索相似任务 |
| `app/api/v1/endpoints/similarity.py:search_similar()` | 语义查重 API（异常时降级返回 `success=false`，不阻塞创建流程） |

## 3. 主要数据链路

```text
任务标题/描述
  -> generate_embedding()
  -> upsert_task_embedding(task_id, text_content)
  -> task_embeddings(vector)
  -> search_similar_tasks()
  -> 相似任务结果（供 API 返回）
```

## 4. 迁移与运维命令

```bash
cd cortex-backend
source .venv/bin/activate
aerich migrate
aerich upgrade
```

说明：
1. 关系表结构由 Aerich 迁移管理。
2. 向量表 `task_embeddings` 由 `init_pgvector()` 负责初始化（包含索引）。

## 5. 模块边界

| 方向 | 边界说明 |
|------|----------|
| 上游调用 | API 路由与服务层调用本模块，不直接操作底层 SQL 细节 |
| 下游依赖 | PostgreSQL + pgvector + embedding 模型（sentence-transformers） |
| 不负责内容 | 鉴权、任务业务状态流转、前端展示逻辑 |
