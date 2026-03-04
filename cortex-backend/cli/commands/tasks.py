import secrets
import webbrowser
import re
import json
import os
import typer
from datetime import datetime
from rich.console import Console
from rich.table import Table
from cli.api import client
from cli.config import (
    get_config_value, DELETE_LOCAL_ON_DONE, DELETE_REMOTE_ON_DONE,
    DELETE_WORKTREE_ON_DONE,
    GIT_PROVIDER, GITHUB_TOKEN, GITLAB_TOKEN, USE_WORKTREE
)
from cli.git import (
    create_branch,
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
    git_pull, delete_local_branch,
    get_diff_for_ai,
    create_worktree,
    remove_worktree,
    run_git_command,
)
from cli.providers import get_provider
from cli.providers.pr_comment import get_pr_comment_provider, ReviewComment
from cli.ai import generate_commit_message, generate_pr_description, review_code
from cli.config import AI_REVIEW_ENABLED

app = typer.Typer()
console = Console()

BRANCH_TYPES = ["feature", "bug", "docs", "fix", "chore", "refactor"]
BRANCH_PATTERN = re.compile(r"(feature|bug|docs|fix|chore|refactor)/task-(\d+)-")

@app.command(name="new")
def create_task(
    title: str = typer.Argument(..., help="任务标题"),
    deadline: str = typer.Argument(..., help="截止日期 (YYYY-MM-DD)"),
    type: str = typer.Option("feature", "--type", "-t", help="任务类型"),
    priority: str = typer.Option("medium", "--priority", "-p", help="优先级"),
    description: str = typer.Option("", "--desc", "-d", help="任务描述"),
):
    """
    新建任务: 通过 cortex-backend API 创建新任务
    """
    api = client()

    try:
        datetime.strptime(deadline, "%Y-%m-%d").date()
    except ValueError:
        console.print(f"[red]Invalid date format. Use YYYY-MM-DD[/red]")
        raise typer.Exit(1)

    project_id = get_config_value("default_project_id")
    if not project_id:
        console.print("[red]Please set default_project_id in config[/red]")
        raise typer.Exit(1)

    task_data = {
        "title": title,
        "project_id": int(project_id),
        "deadline": deadline,
        "priority": priority.upper(),
        "status": "TODO",
    }

    if description:
        task_data["description"] = f"[{type}]\n{description}"
    else:
        task_data["description"] = f"[{type}]"

    try:
        response = api.post("/tasks/", json_data=task_data)
        if response.status_code != 200:
            console.print(f"[red]Failed to create task: {response.text}[/red]")
            raise typer.Exit(1)

        task = response.json()
        console.print(f"[green]✔ Task created successfully![/green]")
        console.print(f"[cyan]Task ID: {task['id']}[/cyan]")
        console.print(f"[cyan]Title: {task['title']}[/cyan]")
        console.print(f"[cyan]Deadline: {task['deadline']}[/cyan]")
    except Exception as e:
        console.print(f"[red]Connection error: {e}[/red]")
        raise typer.Exit(1)

@app.command(name="list")
def list_tasks(json_output: bool = typer.Option(False, "--json", help="以 JSON 格式输出")):
    """
    列出分配给当前用户的任务
    """
    # 1. 初始化 API 客户端
    api = client()

    # 2. 发送请求
    try:
        response = api.get("/tasks/")
        if response.status_code != 200:
            console.print(f"[red]Error fetching tasks: {response.text}[/red]")
            raise typer.Exit(1)

        tasks = response.json()
    except Exception as e:
        console.print(f"[red]Connection error: {e}[/red]")
        raise typer.Exit(1)

    # 3. 处理空数据
    if not tasks:
        if json_output:
            console.print(json.dumps({"tasks": [], "message": "No assigned tasks"}, ensure_ascii=False))
        else:
            console.print("[yellow]You have no assigned tasks. Good job![/yellow]")
        return

    # 4. JSON 输出
    if json_output:
        console.print(json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2))
        return

    # 5. 渲染表格
    table = Table()

    # 定义列
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Priority", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Branch", style="blue")
    # 填充数据
    for task in tasks:
        # 根据优先级设置颜色
        priority_color = "red" if task['priority'] == 'HIGH' else "white"
        branch = task.get('branch_name') or ""
        table.add_row(
            str(task['id']),
            task['title'],
            f"[{priority_color}]{task['priority']}[/{priority_color}]",
            task['status'],
            branch
        )

    console.print(table)

@app.command()
def start(task_id: int, use_worktree: bool = typer.Option(None, "--worktree/--no-worktree", help="是否使用 worktree")):
    """
    开始任务:
    1. 检查/生成随机分支名并绑定到任务
    2. 更新状态为 IN_PROGRESS
    3. 创建 worktree（如果启用）
    4. 切换 Git 分支
    """
    api = client()
    ensure_git_repo()
    console.print(f"[cyan]🚀 Preparing task #{task_id}...[/cyan]")

    response = api.get(f"/tasks/{task_id}")
    if response.status_code == 404:
        console.print(f"[red]Task #{task_id} not found.[/red]")
        raise typer.Exit(1)
    elif response.status_code != 200:
        console.print(f"[red]Error fetching task: {response.text}[/red]")
        raise typer.Exit(1)
    task = response.json()

    branch_name = task.get('branch_name')
    branch_type = task.get('type', 'feature')
    is_new_branch = False
    if not branch_name:
        # 数据库没存，生成新的
        branch_name = generate_random_branch_name(task_id, branch_type)
        is_new_branch = True
        console.print(f"[yellow]⚡ Generated new branch name: {branch_name}[/yellow]")
    else:
        # 数据库有，直接用
        console.print(f"[blue]ℹ️  Using existing branch: {branch_name}[/blue]")

    update_data = {"status": "IN_PROGRESS"}
    if is_new_branch:
        update_data["branch_name"] = branch_name

    patch_resp = api.patch(f"/tasks/{task_id}", json_data=update_data)
    if patch_resp.status_code != 200:
        console.print(f"[red]Failed to update task: {patch_resp.text}[/red]")
        raise typer.Exit(1)

    # 判断是否使用 worktree
    if use_worktree is None:
        use_worktree = get_config_value(USE_WORKTREE, default=True)

    try:
        # 创建 worktree（如果启用）
        if use_worktree:
            # 先创建 worktree（基于主分支创建新分支）
            worktree_path = create_worktree(branch_name, task_id)
            # 切换到 worktree 目录
            os.chdir(worktree_path)
            console.print(f"[green]✔ Switched to worktree: {worktree_path}[/green]")
        else:
            create_branch(branch_name)

        console.print(f"[green]✔ Task updated to IN_PROGRESS[/green]")
        console.print(f"[green]✔ Switched to branch: [bold]{branch_name}[/bold][/green]")
        console.print("[yellow]Happy coding! 💻[/yellow]")
    except typer.Exit as e:
        console.print(str(e))

def _get_git_provider():
    """
    获取 Git Provider 实例

    从 git remote URL 自动识别并获取 Provider

    Returns:
        (provider, repo_url) 元组，如果配置不完整则返回 (None, None)
    """
    provider_type = get_config_value(GIT_PROVIDER)
    remote_url = get_remote_url()

    if not remote_url:
        return None, None

    # 从 remote URL 提取 repo 路径
    from urllib.parse import urlparse
    parsed = urlparse(remote_url)
    repo_path = parsed.path.strip("/")

    if provider_type == "github":
        token = get_config_value(GITHUB_TOKEN)
        if token:
            provider = get_provider("github", token, f"https://github.com/{repo_path}")
            return provider, f"https://github.com/{repo_path}"
    elif provider_type == "gitlab":
        token = get_config_value(GITLAB_TOKEN)
        if token:
            # GitLab 可能是自定义域名
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            provider = get_provider("gitlab", token, f"{base_url}/{repo_path}")
            return provider, f"{base_url}/{repo_path}"

    return None, None


@app.command()
def pr(use_ai: bool = typer.Option(True, "--ai/--no-ai", help="是否使用 AI 生成 commit message 和 PR 描述")):
    """
    提交任务:
    1. 识别当前任务分支
    2. 生成并提交 commit message（可选 AI 辅助）
    3. 更新状态 -> REVIEW
    4. Git Push
    5. 创建 PR/MR 并打开链接
    """
    api = client()
    ensure_git_repo()

    # 1. 获取当前分支
    branch_name = get_current_branch()

    # 2. 从分支名提取任务 ID
    # 匹配模式: {type}/task-{id}-{suffix}
    match = BRANCH_PATTERN.match(branch_name)
    if not match:
        console.print(f"[red]Current branch '{branch_name}' is not a valid Cortex task branch.[/red]")
        console.print(f"Branch name must match '{{type}}/task-{{id}}-{{suffix}}'.")
        console.print(f"Supported types: {', '.join(BRANCH_TYPES)}")
        raise typer.Exit(1)

    task_id = int(match.group(2))

    # 获取任务信息（用于 AI 生成）
    task_resp = api.get(f"/tasks/{task_id}")
    task = task_resp.json() if task_resp.status_code == 200 else {}
    task_title = task.get("title", f"Task #{task_id}")

    # 获取 diff 用于 AI 生成
    diff_for_ai = ""
    if use_ai:
        diff_for_ai = get_diff_for_ai()

    if has_uncommitted_changes():
        console.print("[yellow]⚡ Detected uncommitted changes.[/yellow]")

        # 2.1 执行 git add .
        console.print("Staging all changes...")
        stage_all_changes()

        # 2.2 生成/获取提交信息
        commit_msg = None
        if use_ai and diff_for_ai:
            console.print("[cyan]🤖 Generating commit message with AI...[/cyan]")
            commit_msg = generate_commit_message(diff_for_ai, task_title)
            if commit_msg:
                console.print(f"[green]AI suggested: {commit_msg}[/green]")
                if not typer.confirm("Use this commit message?", default=True):
                    commit_msg = None

        # 如果没有 AI 生成或用户拒绝，让用户输入
        if not commit_msg:
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
    else:
        console.print(f"[green]✔ Task status updated to REVIEW[/green]")

    # 4. 推送代码
    try:
        push_current_branch(branch_name)
        console.print(f"[green]✔ Code pushed to origin[/green]")
    except typer.Exit as e:
        console.print(f"[red]Git push failed: {e}[/red]")
        raise typer.Exit(1)

    # 5. 创建 PR/MR
    provider, repo_url = _get_git_provider()

    if provider:
        target_branch = get_main_branch()
        try:
            title = task.get("title", f"Task #{task_id}")
            is_gitlab = 'gitlab' in repo_url

            # 生成 PR 描述
            if use_ai and diff_for_ai:
                console.print("[cyan]🤖 Generating PR description with AI...[/cyan]")
                pr_description = generate_pr_description(
                    diff=diff_for_ai,
                    task_id=task_id,
                    task_title=task_title,
                    task_type=task.get("type", "feature"),
                    task_description=task.get("description", ""),
                )
            else:
                pr_description = f"Task #{task_id}\n\n{task.get('description', '')}"

            console.print(f"[cyan]Creating {'Merge Request' if is_gitlab else 'Pull Request'}...[/cyan]")

            pr_info = provider.create_pull_request(
                title=title,
                source_branch=branch_name,
                target_branch=target_branch,
                description=pr_description,
            )

            console.print(f"[green]✔ {'MR' if is_gitlab else 'PR'} created successfully![/green]")
            console.print(f"[bold cyan]🔗 {'MR' if is_gitlab else 'PR'} URL:[/bold cyan] {pr_info.url}")

            # 6. AI 代码审查并发布到 PR 评论区（使用当前分支与主分支的差异）
            _publish_review_to_pr(
                pr_info.number,
                diff_for_ai if diff_for_ai else get_diff_for_ai(use_staged=False),
                task_id=task_id,
                api_client=api,
            )

            # 询问是否自动打开浏览器
            if typer.confirm("Open in browser?", default=True):
                webbrowser.open(pr_info.url)

        except RuntimeError as e:
            console.print(f"[yellow]⚠️  {str(e)}[/yellow]")
            console.print("[blue]ℹ️  Falling back to browser link...[/blue]")
            pr_url = f"{repo_url}/compare/{branch_name}?expand=1"
            console.print(f"[bold yellow]🔗 Create PR:[/bold yellow] {pr_url}")
            if typer.confirm("Open in browser?", default=True):
                webbrowser.open(pr_url)
    else:
        # 回退到原有的浏览器链接方式
        remote_url = get_remote_url()
        if remote_url:
            pr_url = f"{remote_url}/compare/{branch_name}?expand=1"
            console.print(f"\n[bold yellow]🔗 Create Pull Request:[/bold yellow] {pr_url}")
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
    3. 删除 worktree（如果使用了 worktree）
    4. 根据配置决定是否删除本地功能分支
    """
    api = client()
    ensure_git_repo()

    # 1. 识别当前任务分支
    feature_branch = get_current_branch()
    match = BRANCH_PATTERN.match(feature_branch)

    if not match:
        console.print(f"[red]Current branch '{feature_branch}' is not a valid Cortex task branch.[/red]")
        console.print(f"Branch name must match '{{type}}/task-{{id}}-{{suffix}}'.")
        console.print(f"Supported types: {', '.join(BRANCH_TYPES)}")
        raise typer.Exit(1)

    task_id = int(match.group(2))
    main_branch = get_main_branch()
    console.print(f"[cyan]🚀 Wrapping up task #{task_id}...[/cyan]")

    # 保存当前工作目录（如果是在 worktree 中）
    original_cwd = os.getcwd()

    try:
        # 切换回 main 分支
        checkout_branch(main_branch)
        git_pull()

        # 更新任务状态为 DONE
        patch_resp = api.patch(f"/tasks/{task_id}", json_data={"status": "DONE"})
        if patch_resp.status_code == 200:
            console.print(f"[green]✔ Task status updated to DONE[/green]")

        # 检查是否需要清理 worktree
        should_delete_worktree = get_config_value(DELETE_WORKTREE_ON_DONE, default=False)

        if should_delete_worktree:
            try:
                # 获取主仓库根目录
                repo_root = run_git_command(["rev-parse", "--show-toplevel"])
                # 如果当前目录不在主仓库中，说明使用了 worktree
                if not original_cwd.startswith(repo_root):
                    worktree_path = original_cwd
                    console.print(f"[cyan]🧹 Cleaning up worktree at {worktree_path}...[/cyan]")
                    remove_worktree(feature_branch, task_id)
                    # 切换回项目目录
                    os.chdir(repo_root)
                    console.print(f"[green]✔ Returned to project directory[/green]")
                else:
                    console.print("[blue]ℹ️  Not in a worktree. Skipping worktree cleanup.[/blue]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not check/cleanup worktree: {e}[/yellow]")
        else:
            if not original_cwd.startswith(run_git_command(["rev-parse", "--show-toplevel"])):
                console.print(f"[blue]ℹ️  Config 'delete_worktree_on_done' is False. Worktree kept at {original_cwd}[/blue]")

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


def generate_random_branch_name(task_id: int, branch_type: str = "feature") -> str:
    """
    生成随机分支名
    格式: {type}/task-{id}-{随机8位字符}
    例如: feature/task-2-a1b2c3d4, bug/task-3-c3d4e5f6
    """
    random_suffix = secrets.token_hex(4)
    return f"{branch_type}/task-{task_id}-{random_suffix}"


def _publish_review_to_pr(pr_number: int, diff: str, task_id: int = None, api_client=None):
    """将 AI 审查结果发布到 PR 评论区"""
    # 检查是否启用 AI 审查
    review_enabled = get_config_value(AI_REVIEW_ENABLED, default=True)
    if not review_enabled:
        return

    if not diff:
        return

    provider_type = get_config_value(GIT_PROVIDER)
    if not provider_type:
        return

    remote_url = get_remote_url()
    if not remote_url:
        return

    # 获取 token
    if provider_type == "github":
        token = get_config_value(GITHUB_TOKEN)
    elif provider_type == "gitee":
        token = get_config_value(GITLAB_TOKEN)
    else:
        return

    if not token:
        return

    try:
        # 执行代码审查
        result = review_code(diff)

        # 获取 PR Comment Provider
        comment_provider = get_pr_comment_provider(provider_type, token, remote_url)

        # 创建审查结果摘要评论
        body = _format_review_for_pr(result)
        comment_provider.create_review_comment(pr_number, body)
        _sync_review_to_task_comment(task_id=task_id, body=body, api_client=api_client)

        # 批量创建详细问题评论
        comments = []
        for issue in result.issues:
            comment = ReviewComment(
                path=issue.file,
                line=issue.line,
                body=f"**[{issue.category}]** {issue.message}\n\n建议: {issue.suggestion or '无'}",
                severity=issue.severity
            )
            comments.append(comment)

        if comments:
            comment_ids = comment_provider.create_review_comments_batch(pr_number, comments)
            console.print(f"[green]✅ 已发布 {len(comment_ids)} 条审查评论到 PR #{pr_number}[/green]")

    except Exception as e:
        console.print(f"[yellow]⚠️  AI 审查发布失败: {e}[/yellow]")


def _sync_review_to_task_comment(task_id: int, body: str, api_client):
    """将审查摘要同步到任务评论（失败降级，不影响主流程）"""
    if not task_id or not body or api_client is None:
        return

    try:
        response = api_client.post(f"/tasks/{task_id}/comments", json_data={"content": body}, timeout=5)
        if response.status_code // 100 != 2:
            console.print(
                f"[yellow]⚠️  审查摘要已发布到 PR，但同步任务评论失败: HTTP {response.status_code}[/yellow]"
            )
    except Exception as e:
        console.print(f"[yellow]⚠️  审查摘要已发布到 PR，但同步任务评论失败: {e}[/yellow]")


def _format_review_for_pr(result) -> str:
    """格式化审查结果为 Markdown 评论"""
    lines = [
        "## AI 代码审查结果",
        "",
        f"**评分**: {result.score}/100",
        "",
        f"**摘要**: {result.summary}",
        "",
        "---",
    ]

    if result.issues:
        lines.extend(["", "### 审查详情", ""])

        # 按 severity 分组
        severity_order = {"error": 0, "warning": 1, "info": 2}
        grouped = {}
        for issue in result.issues:
            key = severity_order.get(issue.severity, 3)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(issue)

        for key in sorted(grouped.keys()):
            severity = {0: "🔴 错误", 1: "🟡 警告", 2: "🔵 信息"}.get(key, "⚪ 其他")
            lines.append(f"#### {severity} ({len(grouped[key])} 项)")
            for issue in grouped[key]:
                lines.append(f"- **{issue.file}:{issue.line}** - {issue.message}")

    return "\n".join(lines)
