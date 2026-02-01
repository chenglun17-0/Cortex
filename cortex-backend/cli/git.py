import os
import subprocess
import typer

from cli.config import GIT_MAIN_BRANCH, get_config_value

def run_git_command(args: list[str]) -> str:
    """运行 git 命令并返回输出"""
    try:
        result = subprocess.run(
            ["git"] + args,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # 如果是 git 报错，抛出异常或处理
        raise typer.Exit(f"Git error: {e.stderr.strip()}")
    except FileNotFoundError:
        raise typer.Exit("Git is not installed or not found in PATH.")

def ensure_git_repo():
    """确保当前目录是 git 仓库"""
    try:
        run_git_command(["rev-parse", "--is-inside-work-tree"])
    except typer.Exit:
        typer.echo("Error: Not a git repository. Please run inside your project folder.")
        raise typer.Exit(1)

def create_branch(branch_name: str):
    """创建并切换到新分支"""
    # 1. 检查分支是否存在
    branch_exists = False
    try:
        # rev-parse --verify 如果成功返回 0，失败抛出异常
        run_git_command(["rev-parse", "--verify", branch_name])
        branch_exists = True
    except Exception:
        branch_exists = False

        # 2. 根据检测结果执行对应操作
    if branch_exists:
        typer.echo(f"Branch '{branch_name}' already exists. Switching...")
        try:
            run_git_command(["checkout", branch_name])
        except Exception as e:
            # 如果切换失败（比如当前有未提交的冲突文件），直接报错，而不是去尝试创建新分支
            typer.echo(f"[red]Failed to switch branch: {e}[/red]")
            raise typer.Exit(1)
    else:
        typer.echo(f"Creating new branch '{branch_name}'...")
        try:
            run_git_command(["checkout", "-b", branch_name])
        except Exception as e:
            typer.echo(f"[red]Failed to create branch: {e}[/red]")
            raise typer.Exit(1)


def get_current_branch() -> str:
    """获取当前所在的分支名"""
    return run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])

def get_main_branch():
    return get_config_value(GIT_MAIN_BRANCH)

def delete_local_branch(branch_name: str):
    """删除本地分支"""
    typer.echo(f"Deleting local branch '{branch_name}'...")
    try:
        run_git_command(["branch", "-d", branch_name])
    except Exception as e:
        typer.echo(f"[yellow]Warning: Could not delete local branch: {e}[/yellow]")

def delete_remote_branch(branch_name: str):
    """删除远程分支"""
    typer.echo(f"Deleting remote branch 'origin/{branch_name}'...")
    try:
        run_git_command(["push", "origin", "--delete", branch_name])
    except Exception as e:
        typer.echo(f"[yellow]Warning: Could not delete remote branch (maybe already deleted?): {e}[/yellow]")

def checkout_branch(branch_name: str):
    """切换到指定分支"""
    typer.echo(f"Switching to {branch_name}...")
    try:
        run_git_command(["checkout", branch_name])
    except Exception as e:
        typer.echo(f"[red]Failed to switch branch: {e}[/red]")

def git_pull():
    """拉取远程分支"""
    branch_name = get_current_branch()
    run_git_command(["pull", "origin", branch_name])

def push_current_branch(branch_name: str):
    """推送当前分支到 origin"""
    typer.echo(f"Pushing {branch_name} to remote...")
    run_git_command(["push", "-u", "origin", branch_name])

def get_remote_url() -> str:
    """获取远程仓库的 URL"""
    try:
        url = run_git_command(["config", "--get", "remote.origin.url"])
        # 处理 SSH 格式 转 HTTPS
        if url.startswith("git@"):
            url = url.replace(":", "/").replace("git@", "https://")
        # 去掉.git后缀
        if url.endswith(".git"):
            url = url[:-4]
        return url.strip()
    except Exception:
        return ""

def has_uncommitted_changes() -> bool:
    """检查当前工作区是否有未提交的更改"""
    # --porcelain 输出机器可读的简洁状态，如果为空说明是干净的
    output = run_git_command(["status", "--porcelain"])
    return bool(output.strip())

def stage_all_changes():
    """执行git add ."""
    run_git_command(["add", "."])

def commit_changes(message: str):
    """执行git commit -m <message>"""
    run_git_command(["commit", "-m", message])

def get_diff() -> str:
    """获取已暂存的变更的 diff"""
    return run_git_command(["diff", "--staged"])

def get_branch_diff(branch: str, base_branch: str = "main") -> str:
    """
    获取两个分支之间的 diff

    Args:
        branch: 源分支名（当前分支）
        base_branch: 目标分支名（主分支）

    Returns:
        diff 字符串
    """
    return run_git_command(["diff", f"{base_branch}...{branch}"])


def get_worktree_base_path() -> str:
    """获取 worktree 的基础路径（项目目录的上一级）"""
    # 获取当前 git 仓库的根目录
    repo_root = run_git_command(["rev-parse", "--show-toplevel"])
    # 返回上一级目录作为 worktree 基础路径
    return os.path.dirname(repo_root)


def get_worktree_path(branch_name: str, task_id: int) -> str:
    """获取指定任务的 worktree 路径"""
    base_path = get_worktree_base_path()
    repo_name = run_git_command(["rev-parse", "--show-toplevel"]).split("/")[-1]
    return os.path.join(base_path, f"{repo_name}-worktree", f"{task_id}-{branch_name}")


def create_worktree(branch_name: str, task_id: int) -> str:
    """创建 worktree 并返回路径（基于主分支创建新分支）"""
    worktree_path = get_worktree_path(branch_name, task_id)

    # 检查 worktree 是否已存在
    if os.path.exists(worktree_path):
        typer.echo(f"Worktree already exists at '{worktree_path}'. Using it...")
        return worktree_path

    # 获取主分支名
    main_branch = get_main_branch()

    typer.echo(f"Creating worktree at '{worktree_path}'...")
    try:
        # 基于主分支创建新的 worktree 分支
        run_git_command(["worktree", "add", worktree_path, "-b", branch_name, main_branch])
        typer.echo(f"[green]✔ Worktree created successfully[/green]")
        return worktree_path
    except Exception as e:
        typer.echo(f"[red]Failed to create worktree: {e}[/red]")
        raise typer.Exit(1)


def remove_worktree(branch_name: str, task_id: int) -> bool:
    """删除 worktree"""
    worktree_path = get_worktree_path(branch_name, task_id)

    if not os.path.exists(worktree_path):
        typer.echo(f"[yellow]Worktree at '{worktree_path}' does not exist. Skipping.[/yellow]")
        return True

    typer.echo(f"Removing worktree at '{worktree_path}'...")
    try:
        # 先切换出 worktree（如果当前在 worktree 中）
        current_branch = get_current_branch()
        if current_branch == branch_name:
            # 切换回主分支
            main_branch = get_main_branch()
            checkout_branch(main_branch)

        # 删除 worktree
        run_git_command(["worktree", "remove", worktree_path])
        typer.echo(f"[green]✔ Worktree removed successfully[/green]")
        return True
    except Exception as e:
        typer.echo(f"[yellow]Warning: Failed to remove worktree: {e}[/yellow]")
        return False

def get_diff_for_ai(max_length: int = 8000, use_staged: bool = True) -> str:
    """
    获取用于 AI 分析的 diff（已过滤敏感信息并截断）

    Args:
        max_length: 最大返回长度
        use_staged: 是否使用暂存的变更，否则使用当前分支与主分支的差异

    Returns:
        过滤和截断后的 diff 字符串
    """
    if use_staged:
        diff = get_diff()
    else:
        from cli.git import get_current_branch, get_main_branch
        current = get_current_branch()
        main = get_main_branch()
        diff = get_branch_diff(current, main)

    if not diff:
        return ""

    # 过滤敏感信息（token、密钥等）
    import re
    # 过滤常见的敏感信息模式
    patterns = [
        (r'(token|key|secret|password|auth|credential)[^\s=]*[\s=]*[^\s\'"]+', r'\1=[FILTERED]'),
        (r'Bearer\s+[^\s\'"]+', 'Bearer [FILTERED]'),
        (r'gh[puro]_[^\s\'"]+', 'gh[puro]_[FILTERED]'),
        (r'gitlab-token[^\s\'"]+', 'gitlab-token=[FILTERED]'),
        (r'AI_API_KEY.*', 'AI_API_KEY=[FILTERED]'),
    ]
    for pattern, repl in patterns:
        diff = re.sub(pattern, repl, diff, flags=re.IGNORECASE)

    # 截断过长的 diff
    if len(diff) > max_length:
        diff = diff[:max_length] + "\n\n... (diff truncated for AI processing)"

    return diff