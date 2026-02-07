"""
向量存储服务 - 基于 pgvector 实现任务语义相似度检索

功能：
1. 生成任务文本的 embedding 向量
2. 存储任务向量到 pgvector
3. 检索相似任务
"""
import logging
from typing import List, Optional
from datetime import datetime

from pgvector.asyncpg import register_vector
import asyncpg

from app.core.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

logger = logging.getLogger(__name__)

# Embedding 模型（使用轻量级模型，本地运行）
_EMBEDDING_MODEL = None
_EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 的维度
_MAX_TEXT_LENGTH = 2000  # 最大文本长度限制

# 数据库连接池
_db_pool: Optional[asyncpg.Pool] = None


def get_embedding_model():
    """获取 embedding 模型（懒加载）"""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBEDDING_MODEL


async def get_db_pool() -> asyncpg.Pool:
    """获取数据库连接池（懒加载）"""
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            min_size=2,
            max_size=10,
        )
    return _db_pool


async def close_db_pool():
    """关闭数据库连接池"""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None


def _truncate_text(text: str, max_length: int = _MAX_TEXT_LENGTH) -> str:
    """截断文本到最大长度"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


async def generate_embedding(text: str) -> List[float]:
    """
    生成文本的 embedding 向量

    Args:
        text: 输入文本（任务标题 + 描述）

    Returns:
        embedding 向量

    Raises:
        RuntimeError: 生成 embedding 失败时抛出
    """
    # 截断过长的文本
    text = _truncate_text(text)

    try:
        model = get_embedding_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"生成 embedding 失败: {e}")
        raise RuntimeError(f"生成 embedding 失败: {e}") from e


async def init_pgvector():
    """
    初始化 pgvector 扩展和表结构

    需要在 PostgreSQL 中先执行: CREATE EXTENSION IF NOT EXISTS vector;
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
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

        logger.info("pgvector 初始化完成")


async def upsert_task_embedding(task_id: int, text_content: str) -> bool:
    """
    存储或更新任务的 embedding 向量

    Args:
        task_id: 任务 ID
        text_content: 任务文本内容（标题 + 描述）

    Returns:
        是否成功
    """
    try:
        embedding = await generate_embedding(text_content)
    except RuntimeError:
        logger.error(f"生成 embedding 失败，跳过存储 (task_id={task_id})")
        return False

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
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
        logger.error(f"存储任务 embedding 失败 (task_id={task_id}): {e}")
        return False


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

    Raises:
        RuntimeError: 生成 embedding 失败时抛出
    """
    try:
        query_embedding = await generate_embedding(text_content)
    except RuntimeError:
        raise

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            await register_vector(conn)

            # 构建查询（使用余弦相似度）
            # 注意：pgvector 的 <=> 返回的是距离（0=相同，2=相反），需要转换为相似度
            sql = """
                SELECT
                    te.task_id,
                    te.embedding <=> $1::vector AS distance,
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
                    AND (te.embedding <=> $1::vector) <= $4
                ORDER BY te.embedding <=> $1::vector ASC
                LIMIT $3
            """
            # distance 范围是 0-2，相似度 = 1 - distance/2
            # threshold 是相似度阈值，转换为 distance 阈值
            distance_threshold = (1 - threshold) * 2

            rows = await conn.fetch(sql, query_embedding, exclude_task_id or 0, limit, distance_threshold)

            results = []
            for row in rows:
                distance = float(row["distance"])  # 距离 0-2
                similarity = 1 - distance / 2  # 转换为相似度 0-1
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
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"搜索相似任务失败: {e}")
        return []


async def delete_task_embedding(task_id: int) -> bool:
    """
    删除任务的 embedding 向量

    Args:
        task_id: 任务 ID

    Returns:
        是否成功
    """
    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM task_embeddings WHERE task_id = $1", task_id)
        return True
    except Exception as e:
        logger.error(f"删除任务 embedding 失败 (task_id={task_id}): {e}")
        return False
