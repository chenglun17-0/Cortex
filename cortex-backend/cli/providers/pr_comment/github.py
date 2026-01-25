"""GitHub PR Comment Provider 实现"""
from typing import Optional
from urllib.parse import urlparse
from github import Github, GithubException

from cli.providers.pr_comment.base import PRCommentProvider, ReviewComment


class GitHubPRCommentProvider(PRCommentProvider):
    """GitHub PR 评论 Provider 实现"""

    def __init__(self, token: str, repo_url: str):
        """
        初始化 GitHub PR Comment Provider

        Args:
            token: GitHub Personal Access Token
            repo_url: 仓库 URL (如 https://github.com/user/repo)
        """
        self.token = token
        self.repo_url = repo_url
        self._client: Github = None
        self._repo = None

    def _get_client(self) -> Github:
        """获取 GitHub 客户端"""
        if self._client is None:
            self._client = Github(self.token)
        return self._client

    def _get_repo(self):
        """获取仓库对象"""
        if self._repo is None:
            parsed = urlparse(self.repo_url)
            path = parsed.path.strip("/")
            self._repo = self._get_client().get_repo(path)
        return self._repo

    def create_review_comment(self, pr_number: int, body: str, path: Optional[str] = None, line: Optional[int] = None) -> str:
        """
        创建 PR 评论

        Args:
            pr_number: PR 编号
            body: 评论内容
            path: 文件路径（行内评论需要）
            line: 行号（行内评论需要）

        Returns:
            评论 ID
        """
        repo = self._get_repo()
        pr = repo.get_pull(pr_number)

        try:
            if path and line:
                # 创建行内评论
                comment = pr.create_review_comment(body, path, line, line)
            else:
                # 创建普通评论
                comment = pr.create_issue_comment(body)
            return str(comment.id)
        except GithubException as e:
            raise RuntimeError(f"Failed to create comment: {e.data.get('message', str(e))}")

    def create_review_comments_batch(self, pr_number: int, comments: list[ReviewComment]) -> list[str]:
        """
        批量创建评论

        Args:
            pr_number: PR 编号
            comments: 评论列表

        Returns:
            评论 ID 列表
        """
        repo = self._get_repo()
        pr = repo.get_pull(pr_number)
        comment_ids = []

        # 按 severity 分组，优先处理高 severity
        severity_order = {"error": 0, "warning": 1, "info": 2}
        sorted_comments = sorted(comments, key=lambda c: severity_order.get(c.severity, 3))

        for comment in sorted_comments:
            try:
                if comment.path and comment.line:
                    c = pr.create_review_comment(comment.body, comment.path, comment.line, comment.line)
                else:
                    c = pr.create_issue_comment(comment.body)
                comment_ids.append(str(c.id))
            except GithubException:
                # 忽略失败的评论
                pass

        return comment_ids

    def delete_comment(self, comment_id: str) -> bool:
        """删除评论"""
        repo = self._get_repo()

        try:
            comment = repo.get_comment(int(comment_id))
            comment.delete()
            return True
        except GithubException:
            return False
