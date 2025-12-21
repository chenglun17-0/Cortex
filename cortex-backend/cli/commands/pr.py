import re
import typer
import webbrowser
from rich.console import Console
from cli.api import client
from cli.git import ensure_git_repo, get_current_branch, push_current_branch, get_remote_url

app = typer.Typer()
console = Console()


@app.command()
def create():
    """
    提交任务:
    1. 识别当前任务分支
    2. 更新状态 -> REVIEW
    3. Git Push
    4. 打开 PR 链接
    """
    api = client()
    ensure_git_repo()

    # 1. 获取当前分支
    branch_name = get_current_branch()

    # 2. 从分支名提取任务 ID
    # 匹配模式: feature/task-{id}-{suffix}
    match = re.match(r"feature/task-(\d+)-", branch_name)
    if not match:
        console.print(f"[red]Current branch '{branch_name}' is not a valid Cortex task branch.[/red]")
        console.print("Branch name must start with 'feature/task-{id}-'.")
        raise typer.Exit(1)

    task_id = int(match.group(1))
    console.print(f"[cyan]🚀 Submitting task #{task_id}...[/cyan]")

    # 3. 更新后端状态为 REVIEW
    patch_resp = api.patch(f"/tasks/{task_id}", json_data={"status": "REVIEW"})

    if patch_resp.status_code != 200:
        console.print(f"[red]Failed to update task status: {patch_resp.text}[/red]")
        # 这里不退出，因为即使 API 失败，用户可能还是想 push 代码
    else:
        console.print(f"[green]✔ Task status updated to REVIEW[/green]")

    # 4. 推送代码
    try:
        push_current_branch(branch_name)
        console.print(f"[green]✔ Code pushed to origin[/green]")
    except typer.Exit as e:
        console.print(f"[red]Git push failed: {e}[/red]")
        raise typer.Exit(1)

    # 5. 生成并打开 PR 链接 (以 GitHub 为例)
    remote_url = get_remote_url()
    if remote_url:
        # GitHub PR 快速创建链接格式
        pr_url = f"{remote_url}/compare/{branch_name}?expand=1"
        console.print(f"\n[bold yellow]🔗 Create Pull Request:[/bold yellow] {pr_url}")

        # 询问是否自动打开浏览器
        if typer.confirm("Open in browser?", default=True):
            webbrowser.open(pr_url)
    else:
        console.print("[yellow]Could not detect remote URL. Please open PR manually.[/yellow]")