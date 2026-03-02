import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.api.v1.endpoints import tasks as tasks_endpoint
from app.schemas.task import TaskCommentCreate


class _FakeCommentQuerySet:
    def __init__(self, comments):
        self.comments = comments
        self.order_args = None
        self.offset_value = None
        self.limit_value = None
        self.prefetch_value = None

    async def count(self):
        return len(self.comments)

    def order_by(self, *args):
        self.order_args = args
        return self

    def offset(self, value):
        self.offset_value = value
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def prefetch_related(self, value):
        self.prefetch_value = value
        return self

    async def all(self):
        return self.comments


class _FakeComment:
    def __init__(self):
        self.fetch_related = AsyncMock()


class TaskCommentEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_task_comments_orders_by_newest_first(self):
        fake_comments = [SimpleNamespace(id=2), SimpleNamespace(id=1)]
        fake_qs = _FakeCommentQuerySet(fake_comments)
        current_user = SimpleNamespace(id=100)

        with patch.object(tasks_endpoint, "_ensure_task_access", AsyncMock()) as ensure_access, patch.object(
            tasks_endpoint.TaskComment, "filter", return_value=fake_qs
        ) as filter_mock:
            result = await tasks_endpoint.get_task_comments(
                task_id=10,
                page=2,
                page_size=5,
                current_user=current_user,
            )

        ensure_access.assert_awaited_once_with(task_id=10, current_user=current_user)
        filter_mock.assert_called_once_with(task_id=10)
        self.assertEqual(fake_qs.order_args, ("-created_at", "-id"))
        self.assertEqual(fake_qs.offset_value, 5)
        self.assertEqual(fake_qs.limit_value, 5)
        self.assertEqual(fake_qs.prefetch_value, "author")
        self.assertEqual(result["items"], fake_comments)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["page"], 2)
        self.assertEqual(result["page_size"], 5)

    async def test_create_task_comment_trims_content_before_persist(self):
        current_user = SimpleNamespace(id=7)
        fake_comment = _FakeComment()

        with patch.object(tasks_endpoint, "_ensure_task_access", AsyncMock()), patch.object(
            tasks_endpoint.TaskComment, "create", AsyncMock(return_value=fake_comment)
        ) as create_mock:
            result = await tasks_endpoint.create_task_comment(
                task_id=88,
                comment_in=TaskCommentCreate(content="  hello world  "),
                current_user=current_user,
            )

        create_mock.assert_awaited_once_with(
            content="hello world",
            task_id=88,
            author_id=7,
        )
        fake_comment.fetch_related.assert_awaited_once_with("author")
        self.assertIs(result, fake_comment)

    async def test_create_task_comment_rejects_blank_content(self):
        current_user = SimpleNamespace(id=7)

        with patch.object(tasks_endpoint, "_ensure_task_access", AsyncMock()):
            with self.assertRaises(HTTPException) as context:
                await tasks_endpoint.create_task_comment(
                    task_id=88,
                    comment_in=TaskCommentCreate(content="   "),
                    current_user=current_user,
                )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Comment content cannot be empty")


if __name__ == "__main__":
    unittest.main()
