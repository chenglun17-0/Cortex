import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import typer

from cli.commands import tasks as tasks_command


class TaskDeleteCommandTests(unittest.TestCase):
    def test_delete_task_calls_api_after_confirmation(self):
        api_client = Mock()
        api_client.delete.return_value = SimpleNamespace(status_code=200)

        with patch.object(tasks_command, "client", return_value=api_client), patch.object(
            tasks_command.typer, "confirm", return_value=True
        ) as confirm_mock, patch.object(tasks_command.console, "print") as print_mock:
            tasks_command.delete_task_by_id(9)

        confirm_mock.assert_called_once_with("Delete this task?", default=False)
        api_client.delete.assert_called_once_with("/tasks/9")
        self.assertTrue(
            any("deleted successfully" in str(call.args[0]) for call in print_mock.call_args_list)
        )

    def test_delete_task_stops_when_user_cancels(self):
        api_client = Mock()

        with patch.object(tasks_command, "client", return_value=api_client), patch.object(
            tasks_command.typer, "confirm", return_value=False
        ), patch.object(tasks_command.console, "print") as print_mock:
            with self.assertRaises(typer.Exit) as context:
                tasks_command.delete_task_by_id(9)

        self.assertEqual(context.exception.exit_code, 0)
        api_client.delete.assert_not_called()
        self.assertTrue(
            any("Deletion cancelled" in str(call.args[0]) for call in print_mock.call_args_list)
        )

    def test_delete_task_shows_api_error_details(self):
        api_client = Mock()
        api_client.delete.return_value = SimpleNamespace(
            status_code=404,
            json=lambda: {"detail": "Task not found"},
            text='{"detail":"Task not found"}',
        )

        with patch.object(tasks_command, "client", return_value=api_client), patch.object(
            tasks_command.typer, "confirm", return_value=True
        ), patch.object(tasks_command.console, "print") as print_mock:
            with self.assertRaises(typer.Exit) as context:
                tasks_command.delete_task_by_id(9)

        self.assertEqual(context.exception.exit_code, 1)
        self.assertTrue(
            any("Task not found" in str(call.args[0]) for call in print_mock.call_args_list)
        )


if __name__ == "__main__":
    unittest.main()
