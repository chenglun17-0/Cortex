import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.api.v1.endpoints import similarity as similarity_endpoint
from app.schemas.similarity import SimilaritySearchRequest


class _FakeCommentQuerySet:
    def __init__(self, comments):
        self.comments = comments
        self.order_args = None
        self.limit_value = None

    def order_by(self, *args):
        self.order_args = args
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    async def all(self):
        return self.comments


class SimilarityEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_build_recommendation_combines_description_and_latest_comments(self):
        fake_comments = [
            SimpleNamespace(content=" 优先修复鉴权头格式 "),
            SimpleNamespace(content="补充回归测试，覆盖 401 场景"),
        ]
        fake_qs = _FakeCommentQuerySet(fake_comments)

        with patch.object(similarity_endpoint.TaskComment, "filter", return_value=fake_qs) as filter_mock:
            recommendation = await similarity_endpoint._build_recommendation(
                task_id=8,
                description="修复登录接口超时问题",
            )

        filter_mock.assert_called_once_with(task_id=8)
        self.assertEqual(fake_qs.order_args, ("-created_at", "-id"))
        self.assertEqual(fake_qs.limit_value, 2)
        self.assertIn("修复登录接口超时问题", recommendation)
        self.assertIn("优先修复鉴权头格式", recommendation)

    async def test_search_similar_includes_recommendation_field(self):
        current_user = SimpleNamespace(id=1)
        request = SimilaritySearchRequest(text="登录失败", limit=2, threshold=0.5)
        fake_results = [
            {
                "task_id": 11,
                "title": "修复登录",
                "description": "修复 token 解析",
                "status": "DONE",
                "priority": "HIGH",
                "project_id": 3,
                "similarity": 0.82,
                "created_at": None,
            }
        ]

        with patch.object(similarity_endpoint, "search_similar_tasks", AsyncMock(return_value=fake_results)), patch.object(
            similarity_endpoint, "_build_recommendation", AsyncMock(return_value="建议先校验 token 格式")
        ) as recommendation_mock:
            response = await similarity_endpoint.search_similar(request=request, current_user=current_user)

        recommendation_mock.assert_awaited_once_with(task_id=11, description="修复 token 解析")
        self.assertTrue(response.success)
        self.assertEqual(response.total, 1)
        self.assertEqual(response.results[0].task_id, 11)
        self.assertEqual(response.results[0].recommendation, "建议先校验 token 格式")

    async def test_search_similar_keeps_results_when_recommendation_fails(self):
        current_user = SimpleNamespace(id=1)
        request = SimilaritySearchRequest(text="登录失败", limit=2, threshold=0.5)
        fake_results = [
            {
                "task_id": 11,
                "title": "修复登录",
                "description": "修复 token 解析",
                "status": "DONE",
                "priority": "HIGH",
                "project_id": 3,
                "similarity": 0.82,
                "created_at": None,
            }
        ]

        with patch.object(similarity_endpoint, "search_similar_tasks", AsyncMock(return_value=fake_results)), patch.object(
            similarity_endpoint, "_build_recommendation", AsyncMock(side_effect=RuntimeError("db down"))
        ):
            response = await similarity_endpoint.search_similar(request=request, current_user=current_user)

        self.assertTrue(response.success)
        self.assertEqual(response.total, 1)
        self.assertEqual(response.results[0].task_id, 11)
        self.assertIsNone(response.results[0].recommendation)


if __name__ == "__main__":
    unittest.main()
