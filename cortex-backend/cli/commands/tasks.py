import secrets

import typer
from rich.console import Console
from rich.table import Table
from cli.api import client
from cli.git import ensure_git_repo, create_branch

app = typer.Typer()
console = Console()

@app.command(name="list")
def list_tasks():
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
        console.print("[yellow]You have no assigned tasks. Good job![/yellow]")
        return

    # 4. 渲染表格
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
def go(task_id: int):
    """
    开始任务:
    1. 检查/生成随机分支名并绑定到任务
    2. 更新状态为 IN_PROGRESS
    3. 切换 Git 分支
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
    is_new_branch = False
    if not branch_name:
        # 数据库没存，生成新的
        branch_name = generate_random_branch_name(task_id)
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
    try:
        create_branch(branch_name)
        console.print(f"[green]✔ Task updated to IN_PROGRESS[/green]")
        console.print(f"[green]✔ Switched to branch: [bold]{branch_name}[/bold][/green]")
        console.print("[yellow]Happy coding! 💻[/yellow]")
    except typer.Exit as e:
        console.print(str(e))

def generate_random_branch_name(task_id: int) -> str:
    """
    生成随机分支名
    格式: feature/task-{id}-{随机8位字符}
    例如: feature/task-2-a1b2c3d4
    """
    random_suffix = secrets.token_hex(4) # 生成8位 hex 字符串
    return f"feature/task-{task_id}-{random_suffix}"