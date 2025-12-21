import typer
from rich.console import Console
from rich.table import Table
from cli.api import client

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

    # 填充数据
    for task in tasks:
        # 根据优先级设置颜色
        priority_color = "red" if task['priority'] == 'HIGH' else "white"

        table.add_row(
            str(task['id']),
            task['title'],
            f"[{priority_color}]{task['priority']}[/{priority_color}]",
            task['status']
        )

    console.print(table)