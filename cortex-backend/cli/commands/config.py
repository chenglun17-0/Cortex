import typer
from rich.console import Console
from rich.table import Table
from urllib.parse import urlparse
from cli.config import (
    set_config_value, _load_full_config, get_config_value,
    API_URL, GIT_MAIN_BRANCH, ACCESS_TOKEN,
    DELETE_LOCAL_ON_DONE, DELETE_REMOTE_ON_DONE,
    DELETE_WORKTREE_ON_DONE,
    GIT_PROVIDER, GITHUB_TOKEN, GITLAB_TOKEN,
    AI_PROVIDER, AI_API_KEY, AI_MODEL, AI_BASE_URL,
    USE_WORKTREE,
)

app = typer.Typer()
console = Console()

BOOL_KEYS = {
    DELETE_LOCAL_ON_DONE,
    DELETE_REMOTE_ON_DONE,
    DELETE_WORKTREE_ON_DONE,
    USE_WORKTREE,
}
INT_KEYS = {"default_project_id"}
GIT_PROVIDER_OPTIONS = {"github", "gitlab"}
AI_PROVIDER_OPTIONS = {"openai", "anthropic", "local"}

# 所有可用配置项
CONFIG_KEYS = {
    "url": "后端 API 地址",
    "git_main_branch": "主分支名称 (如 main, master)",
    "default_project_id": "默认项目 ID（用于 ctx tasks new）",
    "access_token": "Cortex 后端访问令牌",
    "delete_local_on_done": "完成任务后删除本地分支",
    "delete_remote_on_done": "完成任务后删除远程分支",
    "delete_worktree_on_done": "完成任务后删除 worktree",
    "use_worktree": "是否默认启用 worktree 模式",
    "git_provider": "Git 提供商 (github/gitlab)",
    "github_token": "GitHub Personal Access Token",
    "gitlab_token": "GitLab Personal Access Token",
    "ai_provider": "AI 提供商 (openai/anthropic/local)",
    "ai_api_key": "AI API Key",
    "ai_model": "AI 模型名称",
    "ai_base_url": "AI API 基础 URL (用于本地模型或反向代理)",
}


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _parse_value(key: str, value: str):
    normalized = value.strip()

    if key in BOOL_KEYS:
        lowered = normalized.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        console.print(f"[red]Invalid boolean value for '{key}': {value}. Use true/false.[/red]")
        raise typer.Exit(1)

    if key in INT_KEYS:
        if normalized.isdigit():
            return int(normalized)
        console.print(f"[red]Invalid integer value for '{key}': {value}[/red]")
        raise typer.Exit(1)

    if normalized.lower() == "true":
        return True
    if normalized.lower() == "false":
        return False
    if normalized.isdigit():
        return int(normalized)
    return normalized


def _validate_value(key: str, value):
    if key == GIT_PROVIDER:
        if not isinstance(value, str):
            console.print("[red]git_provider must be a string.[/red]")
            raise typer.Exit(1)
        value = value.lower()
        if value not in GIT_PROVIDER_OPTIONS:
            console.print(f"[red]Invalid git_provider: {value}. Supported: github/gitlab[/red]")
            raise typer.Exit(1)
        return value

    if key == AI_PROVIDER:
        if not isinstance(value, str):
            console.print("[red]ai_provider must be a string.[/red]")
            raise typer.Exit(1)
        value = value.lower()
        if value not in AI_PROVIDER_OPTIONS:
            console.print("[red]Invalid ai_provider. Supported: openai/anthropic/local[/red]")
            raise typer.Exit(1)
        if value == "local" and not get_config_value(AI_BASE_URL):
            console.print("[yellow]Warning: ai_provider=local 建议同时配置 ai_base_url[/yellow]")
        return value

    if key in {API_URL, AI_BASE_URL}:
        if not isinstance(value, str) or not _is_http_url(value):
            console.print(f"[red]Invalid URL for '{key}'. Use http:// or https://[/red]")
            raise typer.Exit(1)
        return value

    if key in {GIT_MAIN_BRANCH, ACCESS_TOKEN, GITHUB_TOKEN, GITLAB_TOKEN, AI_API_KEY, AI_MODEL}:
        if not isinstance(value, str) or not value.strip():
            console.print(f"[red]'{key}' cannot be empty.[/red]")
            raise typer.Exit(1)
        return value

    return value


@app.command("list")
def list_config():
    """列出当前所有配置"""
    data = _load_full_config()
    table = Table()
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="magenta")

    for key, value in data.items():
        table.add_row(key, str(value))

    console.print(table)

@app.command("keys")
def list_config_keys():
    """列出所有可用的配置项"""
    table = Table()
    table.add_column("Key", style="cyan")
    table.add_column("Description", style="magenta")

    for key, desc in CONFIG_KEYS.items():
        table.add_row(key, desc)

    console.print(table)

@app.command("set")
def set_config(key: str, value: str):
    """
    设置配置项.
    会自动尝试将 "true"/"false" 转为布尔值，数字转为 int。
    """
    real_value = _parse_value(key, value)
    real_value = _validate_value(key, real_value)

    set_config_value(key, real_value)
    console.print(f"[green]✔ Config updated: {key} = {real_value}[/green]")
