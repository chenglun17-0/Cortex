import unittest
from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.api.v1.endpoints import tasks as tasks_endpoint


class TaskSoftDeleteEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_read_my_tasks_filters_soft_deleted_records(self):
        current_user = SimpleNamespace(id=11)
        fake_tasks = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
        fake_qs = SimpleNamespace(all=AsyncMock(return_value=fake_tasks))

        with patch.object(tasks_endpoint.Task, "filter", return_value=fake_qs) as filter_mock:
            result = await tasks_endpoint.read_my_tasks(current_user=current_user)

        filter_mock.assert_called_once_with(assignee=current_user, deleted_at__isnull=True)
        self.assertEqual(result, fake_tasks)

    async def test_get_project_tasks_filters_soft_deleted_records(self):
        current_user = SimpleNamespace(id=11)
        fake_tasks = [SimpleNamespace(id=3)]
        fake_qs = SimpleNamespace(all=AsyncMock(return_value=fake_tasks))

        with patch.object(tasks_endpoint, "_ensure_project_access", AsyncMock()) as ensure_project_access, patch.object(
            tasks_endpoint.Task, "filter", return_value=fake_qs
        ) as filter_mock:
            result = await tasks_endpoint.get_project_tasks(project_id=7, current_user=current_user)

        ensure_project_access.assert_awaited_once_with(project_id=7, current_user=current_user)
        filter_mock.assert_called_once_with(project_id=7, deleted_at__isnull=True)
        self.assertEqual(result, fake_tasks)

    async def test_restore_task_clears_deleted_at_and_rebuilds_embedding(self):
        current_user = SimpleNamespace(id=5)
        deleted_time = datetime.now(UTC)
        fake_task = SimpleNamespace(
            id=42,
            title="Fix login",
            description="repair oauth callback",
            deleted_at=deleted_time,
            save=AsyncMock(),
        )

        with patch.object(tasks_endpoint, "_ensure_task_restore_access", AsyncMock(return_value=fake_task)) as ensure_access, patch.object(
            tasks_endpoint, "upsert_task_embedding", AsyncMock(return_value=True)
        ) as upsert_embedding:
            result = await tasks_endpoint.restore_task(task_id=42, current_user=current_user)

        ensure_access.assert_awaited_once_with(task_id=42, current_user=current_user)
        self.assertIsNone(fake_task.deleted_at)
        fake_task.save.assert_awaited_once()
        upsert_embedding.assert_awaited_once_with(42, "Fix login\nrepair oauth callback")
        self.assertEqual(result, {"message": "Task restored successfully"})

    async def test_restore_task_rejects_non_deleted_task(self):
        current_user = SimpleNamespace(id=5)
        fake_task = SimpleNamespace(
            id=42,
            title="Fix login",
            description=None,
            deleted_at=None,
            save=AsyncMock(),
        )

        with patch.object(tasks_endpoint, "_ensure_task_restore_access", AsyncMock(return_value=fake_task)):
            with self.assertRaises(HTTPException) as context:
                await tasks_endpoint.restore_task(task_id=42, current_user=current_user)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Task is not deleted")

    async def test_restore_task_succeeds_even_if_embedding_rebuild_fails(self):
        current_user = SimpleNamespace(id=5)
        deleted_time = datetime.now(UTC)
        fake_task = SimpleNamespace(
            id=42,
            title="Fix login",
            description="repair oauth callback",
            deleted_at=deleted_time,
            save=AsyncMock(),
        )

        with patch.object(tasks_endpoint, "_ensure_task_restore_access", AsyncMock(return_value=fake_task)), patch.object(
            tasks_endpoint, "upsert_task_embedding", AsyncMock(side_effect=RuntimeError("embedding failed"))
        ):
            result = await tasks_endpoint.restore_task(task_id=42, current_user=current_user)

        self.assertEqual(result, {"message": "Task restored successfully"})
        self.assertIsNone(fake_task.deleted_at)
        fake_task.save.assert_awaited_once()

    async def test_ensure_task_restore_access_rejects_deleted_project_even_for_assignee(self):
        current_user = SimpleNamespace(id=9)
        fake_task = SimpleNamespace(id=8, assignee_id=9, project_id=100)

        with patch.object(tasks_endpoint.Task, "get_or_none", AsyncMock(return_value=fake_task)) as get_task, patch.object(
            tasks_endpoint.Project, "get_or_none", AsyncMock(return_value=None)
        ) as get_project:
            with self.assertRaises(HTTPException) as context:
                await tasks_endpoint._ensure_task_restore_access(task_id=8, current_user=current_user)

        get_task.assert_awaited_once_with(id=8)
        get_project.assert_awaited_once_with(id=100, deleted_at__isnull=True)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Project not found")

    async def test_ensure_task_restore_access_rejects_user_without_project_access(self):
        current_user = SimpleNamespace(id=9)
        fake_task = SimpleNamespace(id=8, assignee_id=1, project_id=100)
        fake_project = SimpleNamespace(owner_id=2)

        with patch.object(tasks_endpoint.Task, "get_or_none", AsyncMock(return_value=fake_task)), patch.object(
            tasks_endpoint.Project, "get_or_none", AsyncMock(return_value=fake_project)
        ), patch.object(tasks_endpoint, "_is_project_member", AsyncMock(return_value=False)):
            with self.assertRaises(HTTPException) as context:
                await tasks_endpoint._ensure_task_restore_access(task_id=8, current_user=current_user)

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "No access to task")


if __name__ == "__main__":
    unittest.main()
