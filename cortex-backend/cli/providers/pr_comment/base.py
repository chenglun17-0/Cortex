"""PR Comment Provider 抽象基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ReviewComment:
    """审查评论"""
    path: str  # 文件路径
    line: int  # 行号
    body: str  # 评论内容
    severity: str = "info"  # severity: info, warning, error


@dataclass
class ReviewResult:
    """审查结果"""
    summary: str  # 审查摘要
    comments: List[ReviewComment] = None  # 详细评论列表

    def __post_init__(self):
        if self.comments is None:
            self.comments = []


class PRCommentProvider(ABC):
    """PR 评论 Provider 抽象基类"""

    @abstractmethod
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
        pass

    @abstractmethod
    def create_review_comments_batch(self, pr_number: int, comments: List[ReviewComment]) -> List[str]:
        """
        批量创建评论

        Args:
            pr_number: PR 编号
            comments: 评论列表

        Returns:
            评论 ID 列表
        """
        pass

    @abstractmethod
    def delete_comment(self, comment_id: str) -> bool:
        """删除评论"""
        pass


def get_pr_comment_provider(provider_type: str, token: str, repo_url: str) -> PRCommentProvider:
    """
    工厂函数：获取对应的 PR Comment Provider

    Args:
        provider_type: "github" 或 "gitee"
        token: API Token
        repo_url: 仓库 URL

    Returns:
        对应的 Provider 实例
    """
    if provider_type == "github":
        from cli.providers.pr_comment.github import GitHubPRCommentProvider
        return GitHubPRCommentProvider(token, repo_url)
    elif provider_type == "gitee":
        from cli.providers.pr_comment.gitee import GiteePRCommentProvider
        return GiteePRCommentProvider(token, repo_url)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
