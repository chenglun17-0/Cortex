import typer
from rich.console import Console
from rich.table import Table
from cli.config import set_config_value, _load_full_config

app = typer.Typer()
console = Console()

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