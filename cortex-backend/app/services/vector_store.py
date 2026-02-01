"""
向量存储服务 - 基于 pgvector 实现任务语义相似度检索

功能：
1. 生成任务文本的 embedding 向量
2. 存储任务向量到 pgvector
3. 检索相似任务
"""
import os
from typing import List, Optional, Tuple
from datetime import datetime

from tortoise.transactions import in_transaction
from pgvector.asyncpg import register_vector
import asyncpg

from app.core.config import settings
from app.models.task import Task


# Embedding 模型（使用轻量级模型，本地运行）
_EMBEDDING_MODEL = None
_EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 的维度


def get_embedding_model():
    """获取 embedding 模型（懒加载）"""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBEDDING_MODEL


async def generate_embedding(text: str) -> List[float]:
    """
    生成文本的 embedding 向量

    Args:
        text: 输入文本（任务标题 + 描述）

    Returns:
        embedding 向量
    """
    try:
        model = get_embedding_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        print(f"[vector_store] 生成 embedding 失败: {e}")
        # 返回零向量作为降级方案
        return [0.0] * _EMBEDDING_DIM


async def init_pgvector():
    """
    初始化 pgvector 扩展和表结构

    需要在 PostgreSQL 中先执行: CREATE EXTENSION IF NOT EXISTS vector;
    """
    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
    )

    try:
        # 注册 vector 类型
        await register_vector(conn)

        # 创建任务向量表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS task_embeddings (
                id SERIAL PRIMARY KEY,
                task_id INTEGER NOT NULL UNIQUE,
                embedding vector(384),
                text_content TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # 创建索引
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_embeddings_vector
            ON task_embeddings USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)

        print("[vector_store] pgvector 初始化完成")
    finally:
        await conn.close()


async def upsert_task_embedding(task_id: int, text_content: str) -> bool:
    """
    存储或更新任务的 embedding 向量

    Args:
        task_id: 任务 ID
        text_content: 任务文本内容（标题 + 描述）

    Returns:
        是否成功
    """
    embedding = await generate_embedding(text_content)

    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
    )

    try:
        await register_vector(conn)

        await conn.execute("""
            INSERT INTO task_embeddings (task_id, embedding, text_content, updated_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (task_id) DO UPDATE SET
                embedding = EXCLUDED.embedding,
                text_content = EXCLUDED.text_content,
                updated_at = EXCLUDED.updated_at
        """, task_id, embedding, text_content, datetime.utcnow())

        return True
    except Exception as e:
        print(f"[vector_store] 存储任务 embedding 失败 (task_id={task_id}): {e}")
        return False
    finally:
        await conn.close()


async def search_similar_tasks(
    text_content: str,
    exclude_task_id: Optional[int] = None,
    limit: int = 5,
    threshold: float = 0.5,
) -> List[dict]:
    """
    搜索相似任务

    Args:
        text_content: 查询文本
        exclude_task_id: 排除的任务 ID（创建新任务时排除自身）
        limit: 返回结果数量
        threshold: 相似度阈值 (0-1)，越高越严格

    Returns:
        相似任务列表，按相似度降序排列
    """
    query_embedding = await generate_embedding(text_content)

    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
    )

    try:
        await register_vector(conn)

        # 构建查询（使用余弦相似度）
        sql = """
            SELECT
                te.task_id,
                te.embedding <=> $1::vector AS similarity,
                te.text_content,
                t.title,
                t.description,
                t.status,
                t.priority,
                t.project_id,
                t.created_at
            FROM task_embeddings te
            JOIN task t ON te.task_id = t.id
            WHERE te.task_id != $2
                AND (t.deleted_at IS NULL)
                AND (te.embedding <=> $1::vector) < $4
            ORDER BY te.embedding <=> $1::vector ASC
            LIMIT $3
        """

        rows = await conn.fetch(sql, query_embedding, exclude_task_id or 0, limit, 1 - threshold)

        results = []
        for row in rows:
            similarity = 1 - float(row["similarity"])  # 转换为相似度 (0-1)
            results.append({
                "task_id": row["task_id"],
                "title": row["title"],
                "description": row["description"],
                "status": row["status"],
                "priority": row["priority"],
                "project_id": row["project_id"],
                "similarity": round(similarity, 3),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            })

        return results
    except Exception as e:
        print(f"[vector_store] 搜索相似任务失败: {e}")
        return []
    finally:
        await conn.close()


async def delete_task_embedding(task_id: int) -> bool:
    """
    删除任务的 embedding 向量

    Args:
        task_id: 任务 ID

    Returns:
        是否成功
    """
    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
    )

    try:
        await conn.execute("DELETE FROM task_embeddings WHERE task_id = $1", task_id)
        return True
    except Exception as e:
        print(f"[vector_store] 删除任务 embedding 失败 (task_id={task_id}): {e}")
        return False
    finally:
        await conn.close()
