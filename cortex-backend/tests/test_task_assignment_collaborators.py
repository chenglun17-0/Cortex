import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.api.v1.endpoints import tasks as tasks_endpoint
from app.schemas.task import TaskCreate, TaskUpdate


class TaskAssignmentCollaboratorTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_task_persists_assignee_and_collaborators(self):
        current_user = SimpleNamespace(id=7)
        project = SimpleNamespace(id=3, owner_id=7)
        task_in = TaskCreate(
            title="实现 AI 代码审查",
            description="支持回写 PR 评论",
            project_id=3,
            assignee_id=9,
            collaborator_ids=[9, 10, 10],
        )
        created_task = SimpleNamespace(id=101)

        with patch.object(tasks_endpoint, "_ensure_project_access", AsyncMock(return_value=project)) as ensure_project_access, patch.object(
            tasks_endpoint, "_get_project_participant_ids", AsyncMock(return_value={7, 9, 10})
        ) as get_participants, patch.object(
            tasks_endpoint.Task, "create", AsyncMock(return_value=created_task)
        ) as task_create, patch.object(
            tasks_endpoint, "_replace_task_collaborators", AsyncMock()
        ) as replace_collaborators, patch.object(
            tasks_endpoint, "upsert_task_embedding", AsyncMock()
        ) as upsert_embedding, patch.object(
            tasks_endpoint, "_serialize_task", return_value={"id": 101, "collaborator_ids": [10]}
        ) as serialize_task:
            result = await tasks_endpoint.create_task(task_in=task_in, current_user=current_user)

        ensure_project_access.assert_awaited_once_with(project_id=3, current_user=current_user)
        get_participants.assert_awaited_once_with(project)
        task_create.assert_awaited_once_with(
            title="实现 AI 代码审查",
            description="支持回写 PR 评论",
            type="feature",
            priority="MEDIUM",
            status="TODO",
            deadline=None,
            project=project,
            assignee_id=9,
        )
        replace_collaborators.assert_awaited_once_with(101, [10])
        upsert_embedding.assert_awaited_once_with(101, "实现 AI 代码审查\n支持回写 PR 评论")
        serialize_task.assert_called_once_with(created_task, [10])
        self.assertEqual(result, {"id": 101, "collaborator_ids": [10]})

    async def test_create_task_rejects_non_project_participant(self):
        current_user = SimpleNamespace(id=7)
        project = SimpleNamespace(id=3, owner_id=7)
        task_in = TaskCreate(
            title="实现 AI 代码审查",
            project_id=3,
            assignee_id=8,
            collaborator_ids=[10],
        )

        with patch.object(tasks_endpoint, "_ensure_project_access", AsyncMock(return_value=project)), patch.object(
            tasks_endpoint, "_get_project_participant_ids", AsyncMock(return_value={7, 8})
        ), patch.object(tasks_endpoint.Task, "create", AsyncMock()) as task_create:
            with self.assertRaises(HTTPException) as ctx:
                await tasks_endpoint.create_task(task_in=task_in, current_user=current_user)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("协同人必须是项目成员或项目负责人", ctx.exception.detail)
        task_create.assert_not_awaited()

    async def test_update_task_updates_assignee_and_collaborators(self):
        current_user = SimpleNamespace(id=7)
        task = SimpleNamespace(
            id=5,
            project_id=3,
            assignee_id=7,
            title="旧标题",
            description="旧描述",
            save=AsyncMock(),
        )
        project = SimpleNamespace(id=3, owner_id=7)
        task_update = TaskUpdate(
            title="新标题",
            assignee_id=8,
            collaborator_ids=[8, 9, 9],
        )

        with patch.object(tasks_endpoint, "_ensure_task_access", AsyncMock(return_value=task)) as ensure_task_access, patch.object(
            tasks_endpoint.Project, "get_or_none", AsyncMock(return_value=project)
        ) as get_project, patch.object(
            tasks_endpoint, "_get_project_participant_ids", AsyncMock(return_value={7, 8, 9})
        ), patch.object(
            tasks_endpoint, "_replace_task_collaborators", AsyncMock()
        ) as replace_collaborators, patch.object(
            tasks_endpoint, "upsert_task_embedding", AsyncMock()
        ) as upsert_embedding, patch.object(
            tasks_endpoint, "_serialize_task", return_value={"id": 5, "assignee_id": 8, "collaborator_ids": [9]}
        ) as serialize_task:
            result = await tasks_endpoint.update_task(
                task_id=5,
                task_update=task_update,
                current_user=current_user,
            )

        ensure_task_access.assert_awaited_once_with(task_id=5, current_user=current_user)
        get_project.assert_awaited_once_with(id=3, deleted_at__isnull=True)
        task.save.assert_awaited_once()
        replace_collaborators.assert_awaited_once_with(5, [9])
        upsert_embedding.assert_awaited_once_with(5, "新标题\n旧描述")
        serialize_task.assert_called_once_with(task, [9])
        self.assertEqual(task.assignee_id, 8)
        self.assertEqual(task.title, "新标题")
        self.assertEqual(result, {"id": 5, "assignee_id": 8, "collaborator_ids": [9]})

    async def test_update_task_only_changes_assignee_keeps_other_collaborators(self):
        current_user = SimpleNamespace(id=7)
        task = SimpleNamespace(
            id=5,
            project_id=3,
            assignee_id=7,
            title="旧标题",
            description="旧描述",
            save=AsyncMock(),
        )
        project = SimpleNamespace(id=3, owner_id=7)
        task_update = TaskUpdate(assignee_id=9)

        with patch.object(tasks_endpoint, "_ensure_task_access", AsyncMock(return_value=task)), patch.object(
            tasks_endpoint.Project, "get_or_none", AsyncMock(return_value=project)
        ), patch.object(
            tasks_endpoint, "_get_task_collaborator_map", AsyncMock(return_value={5: [8, 9]})
        ) as collaborator_map_mock, patch.object(
            tasks_endpoint, "_get_project_participant_ids", AsyncMock(return_value={7, 8, 9})
        ), patch.object(
            tasks_endpoint, "_replace_task_collaborators", AsyncMock()
        ) as replace_collaborators, patch.object(
            tasks_endpoint, "_serialize_task", return_value={"id": 5, "assignee_id": 9, "collaborator_ids": [8]}
        ) as serialize_task:
            result = await tasks_endpoint.update_task(
                task_id=5,
                task_update=task_update,
                current_user=current_user,
            )

        collaborator_map_mock.assert_awaited_once_with([5])
        replace_collaborators.assert_awaited_once_with(5, [8])
        serialize_task.assert_called_once_with(task, [8])
        self.assertEqual(task.assignee_id, 9)
        self.assertEqual(result, {"id": 5, "assignee_id": 9, "collaborator_ids": [8]})

    async def test_ensure_task_access_allows_collaborator(self):
        current_user = SimpleNamespace(id=10)
        task = SimpleNamespace(id=5, assignee_id=7, project_id=3)
        collaborator_qs = SimpleNamespace(exists=AsyncMock(return_value=True))

        with patch.object(tasks_endpoint.Task, "get_or_none", AsyncMock(return_value=task)), patch.object(
            tasks_endpoint.TaskCollaborator, "filter", return_value=collaborator_qs
        ) as collaborator_filter, patch.object(
            tasks_endpoint.Project, "get_or_none", AsyncMock()
        ) as get_project:
            result = await tasks_endpoint._ensure_task_access(task_id=5, current_user=current_user)

        collaborator_filter.assert_called_once_with(task_id=5, user_id=10)
        collaborator_qs.exists.assert_awaited_once_with()
        get_project.assert_not_awaited()
        self.assertEqual(result, task)


if __name__ == "__main__":
    unittest.main()
