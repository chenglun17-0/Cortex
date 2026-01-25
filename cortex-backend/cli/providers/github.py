"""GitHub Provider 实现"""
import re
from urllib.parse import urlparse
from github import Github, GithubException
from github.PullRequest import PullRequest

from cli.providers.base import GitProvider, PRInfo


class GitHubProvider(GitProvider):
    """GitHub Provider 实现"""

    def __init__(self, token: str, repo_url: str):
        """
        初始化 GitHub Provider

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
            # 从 URL 提取 owner/repo
            parsed = urlparse(self.repo_url)
            path = parsed.path.strip("/")
            self._repo = self._get_client().get_repo(path)
        return self._repo

    def create_pull_request(
        self,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str = ""
    ) -> PRInfo:
        """
        创建 GitHub Pull Request

        Args:
            title: PR 标题
            source_branch: 源分支
            target_branch: 目标分支
            description: PR 描述

        Returns:
            PRInfo 对象
        """
        repo = self._get_repo()

        try:
            pr: PullRequest = repo.create_pull(
                title=title,
                body=description,
                head=source_branch,
                base=target_branch
            )

            return PRInfo(
                number=pr.number,
                title=pr.title,
                url=pr.html_url,
                state=pr.state,
                source_branch=pr.head.ref,
                target_branch=pr.base.ref
            )
        except GithubException as e:
            raise RuntimeError(f"Failed to create PR: {e.data.get('message', str(e))}")

    def get_pull_request(self, pr_number: int) -> Optional[PRInfo]:
        """获取 PR 信息"""
        repo = self._get_repo()

        try:
            pr = repo.get_pull(pr_number)
            return PRInfo(
                number=pr.number,
                title=pr.title,
                url=pr.html_url,
                state=pr.state,
                source_branch=pr.head.ref,
                target_branch=pr.base.ref
            )
        except GithubException:
            return None

    def merge_pull_request(self, pr_number: int, commit_message: str = "") -> bool:
        """合并 PR"""
        repo = self._get_repo()

        try:
            pr = repo.get_pull(pr_number)
            if not commit_message:
                commit_message = f"Merge pull request #{pr_number}: {pr.title}"
            pr.merge(commit_message=commit_message)
            return True
        except GithubException as e:
            raise RuntimeError(f"Failed to merge PR #{pr_number}: {e.data.get('message', str(e))}")

    def get_default_branch(self) -> str:
        """获取默认分支"""
        repo = self._get_repo()
        return repo.default_branch

    def is_mergable(self, pr_number: int) -> bool:
        """检查 PR 是否可合并"""
        repo = self._get_repo()

        try:
            pr = repo.get_pull(pr_number)
            return pr.mergeable and pr.state == "open"
        except GithubException:
            return False
