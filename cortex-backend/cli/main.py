import typer

from cli.commands import auth, tasks, config, review

app = typer.Typer(
    name="ctx",
    help="Cortex Project Manager CLI",
    add_completion=False
)
# 注册子命令
app.add_typer(auth.app, name="auth", help="Authentication commands")
app.add_typer(tasks.app, name="tasks", help="Manage tasks")
app.add_typer(config.app, name="config", help="Configuration commands")
app.add_typer(review.app, name="review", help="AI code review commands")

if __name__ == "__main__":
    app()