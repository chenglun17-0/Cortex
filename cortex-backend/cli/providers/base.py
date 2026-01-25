"""Git Provider 抽象基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PRInfo:
    """PR/MR 信息"""
    number: int
    title: str
    url: str
    state: str  # open, closed, merged
    source_branch: str
    target_branch: str


class GitProvider(ABC):
    """Git Provider 抽象基类"""

    @abstractmethod
    def create_pull_request(
        self,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str = ""
    ) -> PRInfo:
        """创建 PR/MR"""
        pass

    @abstractmethod
    def get_pull_request(self, pr_number: int) -> Optional[PRInfo]:
        """获取 PR/MR 信息"""
        pass

    @abstractmethod
    def merge_pull_request(self, pr_number: int, commit_message: str = "") -> bool:
        """合并 PR/MR"""
        pass

    @abstractmethod
    def get_default_branch(self) -> str:
        """获取默认分支名"""
        pass

    @abstractmethod
    def is_mergable(self, pr_number: int) -> bool:
        """检查 PR/MR 是否可合并"""
        pass


def get_provider(provider_type: str, token: str, repo_url: str) -> GitProvider:
    """
    工厂函数：获取对应的 Git Provider

    Args:
        provider_type: "github" 或 "gitlab"
        token: API Token
        repo_url: 仓库 URL (如 https://github.com/user/repo)

    Returns:
        对应的 Provider 实例
    """
    if provider_type == "github":
        from cli.providers.github import GitHubProvider
        return GitHubProvider(token, repo_url)
    elif provider_type == "gitlab":
        from cli.providers.gitlab import GitLabProvider
        return GitLabProvider(token, repo_url)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
