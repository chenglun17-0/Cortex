import typer
import requests
from rich.console import Console
from cli.config import set_config_value, API_URL, ACCESS_TOKEN, get_config_value

console = Console()
app = typer.Typer()
api_url = get_config_value(API_URL)

@app.command()
def login():
    """
    登录到 Cortex 系统并保存凭证
    """
    console.print("[bold blue]Cortex CLI Login[/bold blue]")

    # 1. 交互式获取账号密码
    email = typer.prompt("Email")
    password = typer.prompt("Password", hide_input=True)

    # 2. 发送请求给后端
    try:
        response = requests.post(
            f"{api_url}/login/access-token",
            data={"username": email, "password": password},  # OAuth2 标准表单
        )

        if response.status_code == 200:
            token_data = response.json()
            token = token_data[ACCESS_TOKEN]

            # 3. 保存 Token
            set_config_value(ACCESS_TOKEN, token)
            console.print(f"[green]✔ Login successful! Token saved.[/green]")
        else:
            console.print(f"[red]✘ Login failed: {response.json().get('detail')}[/red]")

    except requests.exceptions.ConnectionError:
        console.print("[red]✘ Could not connect to server. Is it running?[/red]")


@app.command()
def logout():
    """
    注销登录 (删除本地凭证)
    """
    set_config_value(ACCESS_TOKEN, "")
    console.print("[yellow]Logged out successfully.[/yellow]")