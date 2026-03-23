import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from cli.commands import tasks as tasks_command


class TasksReviewSyncTests(unittest.TestCase):
    def _mock_config(self):
        values = {
            tasks_command.AI_REVIEW_ENABLED: True,
            tasks_command.GIT_PROVIDER: "github",
            tasks_command.GITHUB_TOKEN: "token",
        }

        def _get(key, default=None):
            return values.get(key, default)

        return _get

    def test_publish_review_syncs_summary_to_task_comment_when_task_id_is_present(self):
        issue = SimpleNamespace(
            file="app/main.py",
            line=12,
            category="style",
            message="命名可读性不足",
            suggestion="使用语义化变量名",
            severity="warning",
        )
        review_result = SimpleNamespace(score=92, summary="整体实现稳定", issues=[issue])
        provider = Mock()
        provider.create_review_comments_batch.return_value = [101]
        api_client = Mock()
        api_client.post.return_value = SimpleNamespace(status_code=200)

        with patch.object(tasks_command, "get_config_value", side_effect=self._mock_config()), patch.object(
            tasks_command, "get_remote_url", return_value="https://github.com/example/repo"
        ), patch.object(tasks_command, "review_code", return_value=review_result), patch.object(
            tasks_command, "get_pr_comment_provider", return_value=provider
        ), patch.object(tasks_command.console, "print"):
            tasks_command._publish_review_to_pr(8, "diff", task_id=21, api_client=api_client)

        expected_body = tasks_command._format_review_for_pr(review_result)
        provider.create_review_comment.assert_called_once_with(8, expected_body)
        api_client.post.assert_called_once_with(
            "/tasks/21/comments",
            json_data={"content": expected_body},
            timeout=5,
        )

    def test_publish_review_skips_task_comment_sync_without_task_id(self):
        review_result = SimpleNamespace(score=88, summary="通过", issues=[], raw_content="review body")
        provider = Mock()
        api_client = Mock()

        with patch.object(tasks_command, "get_config_value", side_effect=self._mock_config()), patch.object(
            tasks_command, "get_remote_url", return_value="https://github.com/example/repo"
        ), patch.object(tasks_command, "review_code", return_value=review_result), patch.object(
            tasks_command, "get_pr_comment_provider", return_value=provider
        ), patch.object(tasks_command.console, "print"):
            tasks_command._publish_review_to_pr(9, "diff", task_id=None, api_client=api_client)

        api_client.post.assert_not_called()

    def test_publish_review_warns_but_does_not_raise_when_task_comment_sync_fails(self):
        review_result = SimpleNamespace(score=75, summary="存在需关注项", issues=[], raw_content="review body")
        provider = Mock()
        api_client = Mock()
        api_client.post.side_effect = RuntimeError("network error")

        with patch.object(tasks_command, "get_config_value", side_effect=self._mock_config()), patch.object(
            tasks_command, "get_remote_url", return_value="https://github.com/example/repo"
        ), patch.object(tasks_command, "review_code", return_value=review_result), patch.object(
            tasks_command, "get_pr_comment_provider", return_value=provider
        ), patch.object(tasks_command.console, "print") as mock_print:
            tasks_command._publish_review_to_pr(10, "diff", task_id=22, api_client=api_client)

        self.assertTrue(
            any("同步任务评论失败" in str(call.args[0]) for call in mock_print.call_args_list)
        )

    def test_publish_review_warns_when_task_comment_sync_returns_non_2xx(self):
        review_result = SimpleNamespace(score=80, summary="需优化", issues=[], raw_content="review body")
        provider = Mock()
        api_client = Mock()
        api_client.post.return_value = SimpleNamespace(status_code=500)

        with patch.object(tasks_command, "get_config_value", side_effect=self._mock_config()), patch.object(
            tasks_command, "get_remote_url", return_value="https://github.com/example/repo"
        ), patch.object(tasks_command, "review_code", return_value=review_result), patch.object(
            tasks_command, "get_pr_comment_provider", return_value=provider
        ), patch.object(tasks_command.console, "print") as mock_print:
            tasks_command._publish_review_to_pr(11, "diff", task_id=23, api_client=api_client)

        self.assertTrue(
            any("HTTP 500" in str(call.args[0]) for call in mock_print.call_args_list)
        )

    def test_publish_review_accepts_201_when_task_comment_sync_succeeds(self):
        review_result = SimpleNamespace(score=96, summary="表现优秀", issues=[], raw_content="review body")
        provider = Mock()
        api_client = Mock()
        api_client.post.return_value = SimpleNamespace(status_code=201)

        with patch.object(tasks_command, "get_config_value", side_effect=self._mock_config()), patch.object(
            tasks_command, "get_remote_url", return_value="https://github.com/example/repo"
        ), patch.object(tasks_command, "review_code", return_value=review_result), patch.object(
            tasks_command, "get_pr_comment_provider", return_value=provider
        ), patch.object(tasks_command.console, "print") as mock_print:
            tasks_command._publish_review_to_pr(12, "diff", task_id=24, api_client=api_client)

        self.assertFalse(
            any("同步任务评论失败" in str(call.args[0]) for call in mock_print.call_args_list)
        )

    def test_publish_review_skips_when_review_result_has_no_publishable_content(self):
        review_result = SimpleNamespace(
            score=100,
            summary="AI 服务未配置，跳过审查",
            issues=[],
            raw_content="",
        )
        provider = Mock()
        api_client = Mock()

        with patch.object(tasks_command, "get_config_value", side_effect=self._mock_config()), patch.object(
            tasks_command, "get_remote_url", return_value="https://github.com/example/repo"
        ), patch.object(tasks_command, "review_code", return_value=review_result), patch.object(
            tasks_command, "get_pr_comment_provider", return_value=provider
        ), patch.object(tasks_command.console, "print") as mock_print:
            tasks_command._publish_review_to_pr(13, "diff", task_id=25, api_client=api_client)

        provider.create_review_comment.assert_not_called()
        api_client.post.assert_not_called()
        self.assertTrue(
            any("跳过发布 AI 审查" in str(call.args[0]) for call in mock_print.call_args_list)
        )

    def test_publish_review_warns_and_skips_when_review_result_contains_error_summary(self):
        review_result = SimpleNamespace(
            score=100,
            summary="审查出错: 检测到 SOCKS 代理配置，但当前环境未安装代理依赖",
            issues=[],
            raw_content="",
        )
        api_client = Mock()

        with patch.object(tasks_command, "get_config_value", side_effect=self._mock_config()), patch.object(
            tasks_command, "get_remote_url", return_value="https://github.com/example/repo"
        ), patch.object(tasks_command, "review_code", return_value=review_result), patch.object(
            tasks_command, "get_pr_comment_provider"
        ) as mock_provider, patch.object(tasks_command.console, "print") as mock_print:
            tasks_command._publish_review_to_pr(14, "diff", task_id=26, api_client=api_client)

        mock_provider.assert_not_called()
        api_client.post.assert_not_called()
        self.assertTrue(
            any("AI 审查发布失败" in str(call.args[0]) for call in mock_print.call_args_list)
        )


if __name__ == "__main__":
    unittest.main()
