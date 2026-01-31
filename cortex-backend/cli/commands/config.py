import typer
from rich.console import Console
from rich.table import Table
from cli.config import (
    set_config_value, _load_full_config,
    API_URL, GIT_MAIN_BRANCH, ACCESS_TOKEN,
    DELETE_LOCAL_ON_DONE, DELETE_REMOTE_ON_DONE,
    DELETE_WORKTREE_ON_DONE,
    GIT_PROVIDER, GITHUB_TOKEN, GITLAB_TOKEN,
    AI_PROVIDER, AI_API_KEY, AI_MODEL, AI_BASE_URL,
    USE_WORKTREE,
)

app = typer.Typer()
console = Console()

# 所有可用配置项
CONFIG_KEYS = {
    "url": "后端 API 地址",
    "git_main_branch": "主分支名称 (如 main, master)",
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
    # 简单的类型转换逻辑
    if value.lower() == "true":
        real_value = True
    elif value.lower() == "false":
        real_value = False
    elif value.isdigit():
        real_value = int(value)
    else:
        real_value = value

    set_config_value(key, real_value)
    console.print(f"[green]✔ Config updated: {key} = {real_value}[/green]")