import subprocess
import typer

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
    try:
        run_git_command(["rev-parse", "--verify", branch_name])
        # 如果存在，直接切换
        typer.echo(f"Branch '{branch_name}' already exists. Switching...")
        run_git_command(["checkout", branch_name])
    except Exception:
        # 如果不存在，创建并切换
        typer.echo(f"Creating new branch '{branch_name}'...")
        run_git_command(["checkout", "-b", branch_name])