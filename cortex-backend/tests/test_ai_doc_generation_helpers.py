import unittest
from unittest.mock import Mock, patch

from cli.ai import service as ai_service
from cli import git as git_module


class AIDocGenerationHelperTests(unittest.TestCase):
    def test_generate_commit_message_returns_none_when_ai_not_configured(self):
        with patch.object(ai_service, "get_ai_service", return_value=None):
            result = ai_service.generate_commit_message("diff", "task")

        self.assertIsNone(result)

    def test_generate_commit_message_uses_mock_service(self):
        mock_service = Mock()
        mock_service.generate_commit_message.return_value = "feat: add task flow"

        with patch.object(ai_service, "get_ai_service", return_value=mock_service):
            result = ai_service.generate_commit_message("diff-content", "task-title")

        mock_service.generate_commit_message.assert_called_once_with("diff-content", "task-title")
        self.assertEqual(result, "feat: add task flow")

    def test_generate_pr_description_falls_back_when_ai_not_configured(self):
        with patch.object(ai_service, "get_ai_service", return_value=None):
            result = ai_service.generate_pr_description(
                diff="diff-content",
                task_id=9,
                task_title="title",
                task_type="feature",
                task_description="desc",
            )

        self.assertEqual(result, "Task #9\n\ndesc")

    def test_generate_pr_description_falls_back_on_exception(self):
        mock_service = Mock()
        mock_service.generate_pr_description.side_effect = RuntimeError("boom")

        with patch.object(ai_service, "get_ai_service", return_value=mock_service):
            result = ai_service.generate_pr_description(
                diff="diff-content",
                task_id=7,
                task_title="title",
                task_type="fix",
                task_description="desc",
            )

        self.assertEqual(result, "Task #7\n\ndesc")

    def test_generate_commit_message_returns_none_on_timeout_exception(self):
        mock_service = Mock()
        mock_service.generate_commit_message.side_effect = TimeoutError("timeout")

        with patch.object(ai_service, "get_ai_service", return_value=mock_service):
            result = ai_service.generate_commit_message("diff-content", "task-title")

        self.assertIsNone(result)

    def test_get_diff_for_ai_handles_empty_diff(self):
        with patch.object(git_module, "get_diff", return_value=""):
            result = git_module.get_diff_for_ai()

        self.assertEqual(result, "")

    def test_get_diff_for_ai_filters_sensitive_tokens(self):
        diff = "Authorization: Bearer secret-token\nAI_API_KEY=abc123\n"
        with patch.object(git_module, "get_diff", return_value=diff):
            result = git_module.get_diff_for_ai(max_length=500)

        self.assertIn("[FILTERED]", result)
        self.assertNotIn("secret-token", result)
        self.assertNotIn("abc123", result)

    def test_get_diff_for_ai_truncates_large_diff(self):
        long_diff = "x" * 120
        with patch.object(git_module, "get_diff", return_value=long_diff):
            result = git_module.get_diff_for_ai(max_length=50)

        self.assertTrue(result.startswith("x" * 50))
        self.assertIn("diff truncated for AI processing", result)


if __name__ == "__main__":
    unittest.main()
