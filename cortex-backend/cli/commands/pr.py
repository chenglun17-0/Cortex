import re
import typer
import webbrowser
from rich.console import Console
from cli.api import client
from cli.config import get_config_value, DELETE_LOCAL_ON_DONE, DELETE_REMOTE_ON_DONE
from cli.git import (
    ensure_git_repo,
    get_current_branch,
    push_current_branch,
    get_remote_url,
    has_uncommitted_changes,
    stage_all_changes,
    delete_remote_branch,
    commit_changes,
    get_main_branch,
    checkout_branch,
    git_pull, delete_local_branch
)

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

    if has_uncommitted_changes():
        console.print("[yellow]⚡ Detected uncommitted changes.[/yellow]")

        # 2.1 执行 git add .
        console.print("Staging all changes...")
        stage_all_changes()
        # 2.2 让用户输入提交信息
        commit_msg = typer.prompt("Enter commit message")
        # 2.3 执行 commit
        if commit_msg.strip():
            commit_changes(commit_msg)
            console.print("[green]✔ Changes committed.[/green]")
        else:
            console.print("[red]Commit message cannot be empty. Aborting.[/red]")
            raise typer.Exit(1)
    else:
        console.print("[blue]ℹ️  Working tree is clean. Proceeding to push...[/blue]")

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

@app.command()
def done():
    """
    完成任务 (远程已合并):
    1. 切换回 Main 分支并拉取最新代码
    2. 更新任务状态 -> DONE
    3. 根据配置决定是否删除本地功能分支
    """
    api = client()
    ensure_git_repo()

    # 1. 识别当前任务分支
    feature_branch = get_current_branch()
    match = re.match(r"feature/task-(\d+)-", feature_branch)

    if not match:
        console.print(f"[red]Current branch '{feature_branch}' is not a valid Cortex task branch.[/red]")
        raise typer.Exit(1)

    task_id = int(match.group(1))
    main_branch = get_main_branch()
    console.print(f"[cyan]🚀 Wrapping up task #{task_id}...[/cyan]")

    try:
        # 切换回 main 分支
        checkout_branch(main_branch)
        git_pull()
        # 更新任务状态为 DONE
        patch_resp = api.patch(f"/tasks/{task_id}", json_data={"status": "DONE"})
        if patch_resp.status_code == 200:
            console.print(f"[green]✔ Task status updated to DONE[/green]")

        # 读取配置
        should_delete_local = get_config_value(DELETE_LOCAL_ON_DONE, default=False)
        should_delete_remote = get_config_value(DELETE_REMOTE_ON_DONE, default=False)

        if should_delete_local:
            delete_local_branch(feature_branch)
        else:
            console.print(f"[blue]ℹ️  Config 'delete_local_on_done' is False. Local branch kept.[/blue]")

        if should_delete_remote:
            delete_remote_branch(feature_branch)
        else:
            console.print(f"[blue]ℹ️  Config 'delete_remote_on_done' is False. Remote branch kept.[/blue]")

        console.print(f"\n[bold green]🎉 Task #{task_id} Completed![/bold green]")
    except typer.Exit as e:
        raise e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
