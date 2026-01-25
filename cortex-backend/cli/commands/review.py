"""
AI Code Review CLI Command

提供 AI 代码审查功能：
- 审查 PR 中的代码变更
- 将审查结果回写到 PR 评论区
"""
import re
import typer
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from cli.config import (
    get_config_value,
    GIT_PROVIDER,
    GITHUB_TOKEN,
    GITLAB_TOKEN,
    AI_REVIEW_ENABLED,
    AI_REVIEW_DIMENSIONS,
)
from cli.git import (
    ensure_git_repo,
    get_diff_for_ai,
    get_remote_url,
    get_current_branch,
)
from cli.providers import get_provider
from cli.providers.pr_comment import get_pr_comment_provider, ReviewComment
from cli.ai import review_code, get_code_reviewer

app = typer.Typer()
console = Console()

BRANCH_PATTERN = re.compile(r"(feature|bug|docs|fix|chore|refactor)/task-(\d+)-")


def _get_pr_from_branch(branch_name: str, provider) -> Optional[int]:
    """从分支名获取对应的 PR 编号"""
    # GitHub API 方式: 使用 head 参数查询特定分支的 PR
    # 格式: GET /repos/{owner}/{repo}/pulls?head=owner:branch_name
    try:
        # 提取 owner
        remote_url = provider.repo_url
        from urllib.parse import urlparse
        parsed = urlparse(remote_url)
        path = parsed.path.strip("/")  # owner/repo
        owner = path.split("/")[0]

        # 使用 head 参数查询
        prs = provider._repo.get_pulls(state="open", head=f"{owner}:{branch_name}")
        for pr in prs:
            if pr.head.ref == branch_name:
                return pr.number
    except Exception as e:
        console.print(f"[yellow]⚠️  查询 PR 失败: {e}[/yellow]")

    return None


@app.command("run")
def review(
    publish: bool = typer.Option(False, "--publish", "-p", help="将审查结果发布到 PR 评论区"),
):
    """
    AI 代码审查: 审查当前分支的代码变更并发布到 PR 评论区

    可选参数:
        --publish/-p: 将审查结果发布到 PR 评论区

    示例:
        ctx review run           # 只审查当前分支
        ctx review run --publish # 审查并发布到 PR 评论区
    """
    ensure_git_repo()

    # 检查是否启用 AI 审查
    review_enabled = get_config_value(AI_REVIEW_ENABLED, default=True)
    if not review_enabled:
        console.print("[yellow]⚠️  AI 代码审查未启用。请先配置: ctx review status --enable[/yellow]")
        raise typer.Exit(0)

    # 获取当前分支
    branch_name = get_current_branch()

    # 从分支名提取任务 ID
    match = BRANCH_PATTERN.match(branch_name)
    if not match:
        console.print(f"[red]当前分支 '{branch_name}' 不是有效的 Cortex 任务分支[/red]")
        raise typer.Exit(1)

    task_id = int(match.group(2))

    # 获取 diff（当前分支与主分支的差异）
    diff = get_diff_for_ai(use_staged=False)
    if not diff:
        console.print("[yellow]⚠️  没有检测到代码变更[/yellow]")
        raise typer.Exit(0)

    console.print("[cyan]🤖 AI 代码审查中...[/cyan]")

    # 执行审查
    result = review_code(diff)

    # 显示审查摘要
    console.print("\n[bold]审查摘要[/bold]")
    console.print(f"任务 ID: #{task_id}")
    console.print(f"分支: {branch_name}")
    console.print(f"评分: [bold]{result.score}/100[/bold]")
    console.print(f"{result.summary}\n")

    # 显示问题列表
    if result.issues:
        table = Table()
        table.add_column("文件", style="cyan")
        table.add_column("行号", style="magenta", justify="right")
        table.add_column("问题", style="red")
        table.add_column("类别", style="yellow")
        table.add_column("严重程度", style="green")

        for issue in result.issues:
            severity_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(issue.severity, "⚪")
            table.add_row(
                issue.file,
                str(issue.line),
                issue.message[:80] + "..." if len(issue.message) > 80 else issue.message,
                issue.category,
                f"{severity_icon} {issue.severity}"
            )

        console.print(table)
    else:
        console.print("[green]✅ 没有发现代码问题[/green]")

    # 发布到 PR 评论区
    if publish:
        # 获取 PR 编号
        provider_type = get_config_value(GIT_PROVIDER)
        if not provider_type:
            console.print("[yellow]⚠️  未配置 git_provider，无法发布到 PR[/yellow]")
            return

        remote_url = get_remote_url()
        if not remote_url:
            console.print("[yellow]⚠️  无法获取远程仓库 URL[/yellow]")
            return

        # 获取 token
        if provider_type == "github":
            token = get_config_value(GITHUB_TOKEN)
        elif provider_type == "gitee":
            token = get_config_value(GITLAB_TOKEN)
        else:
            console.print(f"[yellow]⚠️  不支持的 provider: {provider_type}[/yellow]")
            return

        if not token:
            console.print("[yellow]⚠️  未配置 API token[/yellow]")
            return

        try:
            from cli.providers.base import PRInfo
            git_provider = get_provider(provider_type, token, remote_url)

            # 获取当前分支对应的 PR
            pr_number = _get_pr_from_branch(branch_name, git_provider)

            if not pr_number:
                console.print(f"[yellow]⚠️  未找到分支 '{branch_name}' 对应的 PR[/yellow]")
                pr_input = typer.prompt("请输入 PR 编号", default="")
                if not pr_input:
                    return
                try:
                    pr_number = int(pr_input)
                except ValueError:
                    console.print("[red]⚠️  PR 编号无效[/red]")
                    return

            _publish_to_pr(pr_number, result)
        except Exception as e:
            console.print(f"[yellow]⚠️  获取 PR 失败: {e}[/yellow]")


def _publish_to_pr(pr_number: int, result):
    """将审查结果发布到 PR 评论区"""
    provider_type = get_config_value(GIT_PROVIDER)
    if not provider_type:
        console.print("[red]⚠️  未配置 git_provider[/red]")
        return

    remote_url = get_remote_url()
    if not remote_url:
        console.print("[red]⚠️  无法获取远程仓库 URL[/red]")
        return

    # 获取 token
    if provider_type == "github":
        token = get_config_value(GITHUB_TOKEN)
    elif provider_type == "gitee":
        token = get_config_value(GITLAB_TOKEN)  # Gitee 也用 gitlab token 配置
    else:
        console.print(f"[red]⚠️  不支持的 provider: {provider_type}[/red]")
        return

    if not token:
        console.print("[red]⚠️  未配置 API token[/red]")
        return

    try:
        comment_provider = get_pr_comment_provider(provider_type, token, remote_url)

        # 构建审查结果摘要评论
        body = _format_review_comment(result)

        # 创建摘要评论
        summary_id = comment_provider.create_review_comment(pr_number, body)
        console.print(f"[green]✅ 已发布审查摘要到 PR #{pr_number}[/green]")

        # 批量创建详细问题评论
        if result.issues:
            comments = []
            for issue in result.issues:
                comment = ReviewComment(
                    path=issue.file,
                    line=issue.line,
                    body=f"**[{issue.category}]** {issue.message}\n\n建议: {issue.suggestion or '无'}",
                    severity=issue.severity
                )
                comments.append(comment)

            comment_ids = comment_provider.create_review_comments_batch(pr_number, comments)
            console.print(f"[green]✅ 已发布 {len(comment_ids)} 条详细审查评论到 PR #{pr_number}[/green]")
        else:
            console.print("[yellow]⚠️  没有发现代码问题，无需发布详细评论[/yellow]")

    except Exception as e:
        console.print(f"[red]⚠️  发布失败: {e}[/red]")


def _format_review_comment(result) -> str:
    """格式化审查结果为 Markdown 评论"""
    lines = [
        "## AI 代码审查结果",
        "",
        f"**评分**: {result.score}/100",
        "",
        f"**摘要**: {result.summary}",
        "",
        "---",
        "",
        "### 审查详情",
    ]

    # 按 severity 分组
    severity_order = {"error": 0, "warning": 1, "info": 2}
    grouped = {}
    for issue in result.issues:
        key = severity_order.get(issue.severity, 3)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(issue)

    for key in sorted(grouped.keys()):
        severity = {0: "错误", 1: "警告", 2: "信息"}.get(key, "其他")
        lines.append(f"\n#### {severity} ({len(grouped[key])} 项)")
        for issue in grouped[key]:
            lines.append(f"- **{issue.file}**:{issue.line} - {issue.message}")

    return "\n".join(lines)


@app.command(name="status")
def review_status(
    enable: Optional[bool] = typer.Option(None, "--enable/--disable", help="启用/禁用 AI 代码审查"),
    show: bool = typer.Option(False, "--show", help="显示当前配置"),
):
    """
    查看/配置 AI 代码审查设置

    示例:
        ctx review status --show          # 显示当前配置
        ctx review status --enable        # 启用 AI 审查
        ctx review status --disable       # 禁用 AI 审查
    """
    if show:
        enabled = get_config_value(AI_REVIEW_ENABLED, default=False)
        dimensions = get_config_value(AI_REVIEW_DIMENSIONS, default=[])

        console.print("[bold]AI 代码审查配置[/bold]")
        console.print(f"启用状态: {'✅ 启用' if enabled else '❌ 禁用'}")
        console.print(f"审查维度: {', '.join(dimensions) if dimensions else '默认全部'}")
        raise typer.Exit(0)

    if enable is not None:
        from cli.config import set_config_value
        set_config_value(AI_REVIEW_ENABLED, enable)
        console.print(f"[green]✅ AI 代码审查已{'启用' if enable else '禁用'}[/green]")
