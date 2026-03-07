import math
import unittest
from datetime import datetime

from app.services import vector_store


class _FakeConn:
    def __init__(self, rows):
        self.rows = rows
        self.last_sql = ""

    async def fetch(self, sql, _exclude_task_id):
        self.last_sql = sql
        return self.rows


class VectorStoreFallbackTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.original_backend = vector_store._EMBEDDING_BACKEND

    def tearDown(self):
        vector_store._EMBEDDING_BACKEND = self.original_backend

    async def test_generate_embedding_uses_hash_backend(self):
        vector_store._EMBEDDING_BACKEND = "hash"
        embedding = await vector_store.generate_embedding("修复登录接口 token 失效")

        self.assertEqual(len(embedding), vector_store._EMBEDDING_DIM)
        norm = math.sqrt(sum(v * v for v in embedding))
        self.assertAlmostEqual(norm, 1.0, places=6)

    async def test_text_fallback_returns_ranked_results(self):
        rows = [
            {
                "task_id": 1,
                "title": "修复登录 token 过期",
                "description": "处理鉴权失败并刷新 token",
                "status": "TODO",
                "priority": "HIGH",
                "project_id": 10,
                "created_at": datetime(2026, 3, 7, 10, 0, 0),
            },
            {
                "task_id": 2,
                "title": "优化项目列表分页",
                "description": "减少查询耗时",
                "status": "IN_PROGRESS",
                "priority": "LOW",
                "project_id": 11,
                "created_at": datetime(2026, 3, 7, 10, 0, 0),
            },
        ]
        conn = _FakeConn(rows)

        results = await vector_store._search_similar_tasks_by_text(
            conn=conn,
            text_content="登录失败 token 过期",
            limit=3,
            threshold=0.2,
        )

        self.assertIn("FROM tasks", conn.last_sql)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["task_id"], 1)
        self.assertGreaterEqual(results[0]["similarity"], 0.2)

    async def test_text_fallback_keeps_high_title_similarity_with_long_description(self):
        rows = [
            {
                "task_id": 3,
                "title": "实现AI代码审查回写PR评论区功能",
                "description": " ".join(["这是一个很长的任务描述"] * 80),
                "status": "TODO",
                "priority": "HIGH",
                "project_id": 12,
                "created_at": datetime(2026, 3, 7, 11, 0, 0),
            },
        ]
        conn = _FakeConn(rows)

        results = await vector_store._search_similar_tasks_by_text(
            conn=conn,
            text_content="实现AI代码审查",
            limit=5,
            threshold=0.5,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["task_id"], 3)
        self.assertGreaterEqual(results[0]["similarity"], 0.5)


if __name__ == "__main__":
    unittest.main()
