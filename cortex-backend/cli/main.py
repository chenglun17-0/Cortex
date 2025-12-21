import typer

from cli.commands import auth, tasks, pr

app = typer.Typer(
    name="ctx",
    help="Cortex Project Manager CLI",
    add_completion=False
)
# 注册子命令
app.add_typer(auth.app, name="auth", help="Authentication commands")
app.add_typer(tasks.app, name="tasks", help="Manage tasks")
app.add_typer(pr.app, name="pr", help="Pull Request workflow")

if __name__ == "__main__":
    app()