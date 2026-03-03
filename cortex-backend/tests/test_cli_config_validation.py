import unittest
from unittest.mock import patch

import typer

from cli.commands import config as config_command


class ConfigCommandValidationTests(unittest.TestCase):
    def test_set_config_accepts_valid_ai_provider_and_normalizes_case(self):
        with patch.object(config_command, "set_config_value") as set_config_value, patch.object(
            config_command.console, "print"
        ):
            config_command.set_config("ai_provider", "OpenAI")

        set_config_value.assert_called_once_with("ai_provider", "openai")

    def test_set_config_rejects_invalid_ai_provider(self):
        with patch.object(config_command, "set_config_value") as set_config_value, patch.object(
            config_command.console, "print"
        ):
            with self.assertRaises(typer.Exit):
                config_command.set_config("ai_provider", "invalid_provider")

        set_config_value.assert_not_called()

    def test_set_config_rejects_invalid_boolean_value_for_use_worktree(self):
        with patch.object(config_command, "set_config_value") as set_config_value, patch.object(
            config_command.console, "print"
        ):
            with self.assertRaises(typer.Exit):
                config_command.set_config("use_worktree", "1")

        set_config_value.assert_not_called()

    def test_set_config_accepts_valid_boolean_value_for_use_worktree(self):
        with patch.object(config_command, "set_config_value") as set_config_value, patch.object(
            config_command.console, "print"
        ):
            config_command.set_config("use_worktree", "true")

        set_config_value.assert_called_once_with("use_worktree", True)

    def test_set_config_rejects_invalid_ai_base_url(self):
        with patch.object(config_command, "set_config_value") as set_config_value, patch.object(
            config_command.console, "print"
        ):
            with self.assertRaises(typer.Exit):
                config_command.set_config("ai_base_url", "localhost:11434")

        set_config_value.assert_not_called()

    def test_set_config_accepts_default_project_id_as_integer(self):
        with patch.object(config_command, "set_config_value") as set_config_value, patch.object(
            config_command.console, "print"
        ):
            config_command.set_config("default_project_id", "123")

        set_config_value.assert_called_once_with("default_project_id", 123)

    def test_set_config_rejects_invalid_api_url(self):
        with patch.object(config_command, "set_config_value") as set_config_value, patch.object(
            config_command.console, "print"
        ):
            with self.assertRaises(typer.Exit):
                config_command.set_config("url", "127.0.0.1:8000")

        set_config_value.assert_not_called()

    def test_set_config_rejects_invalid_git_provider(self):
        with patch.object(config_command, "set_config_value") as set_config_value, patch.object(
            config_command.console, "print"
        ):
            with self.assertRaises(typer.Exit):
                config_command.set_config("git_provider", "gitee")

        set_config_value.assert_not_called()

    def test_set_config_rejects_empty_ai_model(self):
        with patch.object(config_command, "set_config_value") as set_config_value, patch.object(
            config_command.console, "print"
        ):
            with self.assertRaises(typer.Exit):
                config_command.set_config("ai_model", "   ")

        set_config_value.assert_not_called()


if __name__ == "__main__":
    unittest.main()
