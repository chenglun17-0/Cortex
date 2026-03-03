import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.api.v1.endpoints import reports as reports_endpoint


class ReportsEndpointTests(unittest.IsolatedAsyncioTestCase):
    def test_build_overview_report_with_tasks(self):
        tasks = [
            SimpleNamespace(status="TODO", priority="LOW"),
            SimpleNamespace(status="DONE", priority="HIGH"),
            SimpleNamespace(status="DONE", priority="HIGH"),
            SimpleNamespace(status="REVIEW", priority="MEDIUM"),
        ]

        report = reports_endpoint._build_overview_report(total_projects=2, tasks=tasks)

        self.assertEqual(report.total_projects, 2)
        self.assertEqual(report.total_tasks, 4)
        self.assertEqual(report.completed_tasks, 2)
        self.assertEqual(report.completion_rate, 50.0)
        status_map = {item.key: item.count for item in report.status_distribution}
        self.assertEqual(status_map["DONE"], 2)
        self.assertEqual(status_map["TODO"], 1)
        priority_map = {item.key: item.count for item in report.priority_distribution}
        self.assertEqual(priority_map["HIGH"], 2)
        self.assertEqual(priority_map["MEDIUM"], 1)
        self.assertEqual(priority_map["LOW"], 1)

    def test_build_overview_report_with_empty_tasks(self):
        report = reports_endpoint._build_overview_report(total_projects=0, tasks=[])
        self.assertEqual(report.total_projects, 0)
        self.assertEqual(report.total_tasks, 0)
        self.assertEqual(report.completed_tasks, 0)
        self.assertEqual(report.completion_rate, 0.0)

    def test_build_overview_report_normalizes_status_and_priority(self):
        tasks = [
            SimpleNamespace(status="done", priority="high"),
            SimpleNamespace(status=" Done ", priority=" medium "),
            SimpleNamespace(status="custom_status", priority="p0"),
        ]

        report = reports_endpoint._build_overview_report(total_projects=1, tasks=tasks)

        self.assertEqual(report.completed_tasks, 2)
        status_map = {item.key: item.count for item in report.status_distribution}
        priority_map = {item.key: item.count for item in report.priority_distribution}
        self.assertEqual(status_map["DONE"], 2)
        self.assertEqual(status_map["CUSTOM_STATUS"], 1)
        self.assertEqual(priority_map["HIGH"], 1)
        self.assertEqual(priority_map["MEDIUM"], 1)
        self.assertEqual(priority_map["P0"], 1)

    async def test_get_overview_report_returns_zero_when_no_projects(self):
        current_user = SimpleNamespace(id=9)
        project_qs = SimpleNamespace(all=AsyncMock(return_value=[]))

        with patch.object(reports_endpoint.Project, "filter", return_value=project_qs) as project_filter, patch.object(
            reports_endpoint.Task, "filter"
        ) as task_filter:
            report = await reports_endpoint.get_overview_report(current_user=current_user)

        project_filter.assert_called_once_with(members__id=9, deleted_at__isnull=True)
        task_filter.assert_not_called()
        self.assertEqual(report.total_projects, 0)
        self.assertEqual(report.total_tasks, 0)

    async def test_get_overview_report_aggregates_project_tasks(self):
        current_user = SimpleNamespace(id=5)
        projects = [SimpleNamespace(id=1), SimpleNamespace(id=3)]
        tasks = [
            SimpleNamespace(status="TODO", priority="LOW"),
            SimpleNamespace(status="DONE", priority="HIGH"),
        ]
        project_qs = SimpleNamespace(all=AsyncMock(return_value=projects))
        task_qs = SimpleNamespace(all=AsyncMock(return_value=tasks))

        with patch.object(reports_endpoint.Project, "filter", return_value=project_qs) as project_filter, patch.object(
            reports_endpoint.Task, "filter", return_value=task_qs
        ) as task_filter:
            report = await reports_endpoint.get_overview_report(current_user=current_user)

        project_filter.assert_called_once_with(members__id=5, deleted_at__isnull=True)
        task_filter.assert_called_once_with(project_id__in=[1, 3], deleted_at__isnull=True)
        self.assertEqual(report.total_projects, 2)
        self.assertEqual(report.total_tasks, 2)
        self.assertEqual(report.completed_tasks, 1)
        self.assertEqual(report.completion_rate, 50.0)


if __name__ == "__main__":
    unittest.main()
