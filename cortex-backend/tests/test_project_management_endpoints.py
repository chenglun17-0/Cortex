import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException

from app.api.v1.endpoints import projects as projects_endpoint
from app.api.v1.endpoints import users as users_endpoint
from app.schemas.project import ProjectUpdate


class _FakePrefetchAwaitable:
    def __init__(self, items):
        self.items = items
        self.prefetch_args = None

    def prefetch_related(self, *args):
        self.prefetch_args = args
        return self

    def __await__(self):
        async def _inner():
            return self.items

        return _inner().__await__()


class ProjectManagementEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_update_project_updates_fields_and_returns_members(self):
        project = SimpleNamespace(
            id=3,
            name="旧名称",
            description="旧描述",
            owner_id=7,
            organization_id=11,
            created_at=datetime(2026, 1, 1, 0, 0, 0),
            updated_at=datetime(2026, 1, 2, 0, 0, 0),
            save=AsyncMock(),
        )
        member = SimpleNamespace(id=1, username="alice", email="alice@example.com")

        with patch.object(projects_endpoint, "get_project_by_id", AsyncMock(return_value=project)), patch.object(
            projects_endpoint, "_get_project_members", AsyncMock(return_value=[member])
        ):
            result = await projects_endpoint.update_project(
                project_id=3,
                project_in=ProjectUpdate(name="新名称"),
                current_user=SimpleNamespace(id=99),
            )

        project.save.assert_awaited_once()
        self.assertEqual(project.name, "新名称")
        self.assertEqual(result["name"], "新名称")
        self.assertEqual(result["members"], [member])

    async def test_delete_project_rejects_when_project_has_related_tasks(self):
        project = SimpleNamespace(id=8, save=AsyncMock(), deleted_at=None)

        with patch.object(projects_endpoint, "get_project_by_id", AsyncMock(return_value=project)), patch.object(
            projects_endpoint.Task, "filter"
        ) as task_filter:
            task_filter.return_value.count = AsyncMock(return_value=2)

            with self.assertRaises(HTTPException) as ctx:
                await projects_endpoint.delete_project(
                    project_id=8,
                    current_user=SimpleNamespace(id=5),
                )

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("未完成", ctx.exception.detail)
        task_filter.assert_called_once_with(project=project, deleted_at__isnull=True)
        project.save.assert_not_awaited()

    async def test_delete_project_sets_deleted_at_when_no_pending_tasks(self):
        project = SimpleNamespace(id=9, save=AsyncMock(), deleted_at=None)

        with patch.object(projects_endpoint, "get_project_by_id", AsyncMock(return_value=project)), patch.object(
            projects_endpoint.Task, "filter"
        ) as task_filter:
            task_filter.return_value.count = AsyncMock(return_value=0)

            result = await projects_endpoint.delete_project(
                project_id=9,
                current_user=SimpleNamespace(id=5),
            )

        task_filter.assert_called_once_with(project=project, deleted_at__isnull=True)
        project.save.assert_awaited_once()
        self.assertIsInstance(project.deleted_at, datetime)
        self.assertEqual(result["message"], "项目已删除")

    async def test_add_project_member_rejects_duplicate_member(self):
        project = SimpleNamespace(id=2)
        user = SimpleNamespace(id=6)

        with patch.object(projects_endpoint, "get_project_by_id", AsyncMock(return_value=project)), patch.object(
            projects_endpoint.User, "get_or_none", AsyncMock(return_value=user)
        ) as user_get, patch.object(
            projects_endpoint.ProjectMember, "get_or_none", AsyncMock(return_value=SimpleNamespace(id=1))
        ) as member_get:
            with self.assertRaises(HTTPException) as ctx:
                await projects_endpoint.add_project_member(
                    project_id=2,
                    user_id=6,
                    current_user=SimpleNamespace(id=99),
                )

        user_get.assert_awaited_once_with(id=6)
        member_get.assert_awaited_once_with(project=project, user=user)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("已是项目成员", ctx.exception.detail)

    async def test_remove_project_member_rejects_non_member(self):
        project = SimpleNamespace(id=2)

        with patch.object(projects_endpoint, "get_project_by_id", AsyncMock(return_value=project)), patch.object(
            projects_endpoint.ProjectMember, "get_or_none", AsyncMock(return_value=None)
        ) as member_get:
            with self.assertRaises(HTTPException) as ctx:
                await projects_endpoint.remove_project_member(
                    project_id=2,
                    user_id=6,
                    current_user=SimpleNamespace(id=99),
                )

        member_get.assert_awaited_once_with(project=project, user_id=6)
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("不是项目成员", ctx.exception.detail)

    async def test_get_project_members_returns_user_list(self):
        project = SimpleNamespace(id=2)
        memberships = [
            SimpleNamespace(user=SimpleNamespace(id=1, username="alice", email="a@example.com")),
            SimpleNamespace(user=SimpleNamespace(id=2, username="bob", email="b@example.com")),
        ]
        fake_qs = _FakePrefetchAwaitable(memberships)

        with patch.object(projects_endpoint, "get_project_by_id", AsyncMock(return_value=project)), patch.object(
            projects_endpoint.ProjectMember, "filter", return_value=fake_qs
        ):
            result = await projects_endpoint.get_project_members(
                project_id=2,
                current_user=SimpleNamespace(id=99),
            )

        self.assertEqual(fake_qs.prefetch_args, ("user",))
        self.assertEqual([item.username for item in result], ["alice", "bob"])

    async def test_search_users_filters_by_keyword_and_limit(self):
        users = [SimpleNamespace(id=1, username="john_doe", email="john@example.com")]
        qs_after_limit = SimpleNamespace(all=AsyncMock(return_value=users))
        qs = SimpleNamespace(limit=Mock(return_value=qs_after_limit))

        with patch.object(users_endpoint.UserModel, "filter", return_value=qs) as filter_mock:
            result = await users_endpoint.search_users(
                q="john",
                current_user=SimpleNamespace(id=9),
            )

        filter_mock.assert_called_once_with(username__icontains="john")
        qs.limit.assert_called_once_with(20)
        self.assertEqual(result, users)


if __name__ == "__main__":
    unittest.main()
