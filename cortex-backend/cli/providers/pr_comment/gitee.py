"""Gitee PR Comment Provider 实现"""
import requests
from typing import Optional
from urllib.parse import urlparse

from cli.providers.pr_comment.base import PRCommentProvider, ReviewComment


class GiteePRCommentProvider(PRCommentProvider):
    """Gitee PR 评论 Provider 实现"""

    BASE_URL = "https://gitee.com/api/v5"

    def __init__(self, token: str, repo_url: str):
        """
        初始化 Gitee PR Comment Provider

        Args:
            token: Gitee Personal Access Token
            repo_url: 仓库 URL (如 https://gitee.com/user/repo)
        """
        self.token = token
        self.repo_url = repo_url
        self._owner = None
        self._repo = None

    def _parse_repo_url(self) -> tuple[str, str]:
        """解析仓库 URL 获取 owner 和 repo 名"""
        if self._owner is None:
            parsed = urlparse(self.repo_url)
            path = parsed.path.strip("/").split("/")
            self._owner = path[0]
            self._repo = path[1]
        return self._owner, self._repo

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """发送 API 请求"""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Authorization": f"token {self.token}"}
        headers.update(kwargs.pop("headers", {}))
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            **kwargs
        )
        if not response.ok:
            raise RuntimeError(f"Gitee API error: {response.text}")
        return response.json()

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
        owner, repo = self._parse_repo_url()

        if path and line:
            # 行内评论（使用 pull_request_comments API）
            endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/comments"
            data = {
                "body": body,
                "path": path,
                "line": str(line),
                "commit_id": self._get_pr_head_commit(pr_number)
            }
        else:
            # 普通评论（使用 issue_comments API）
            endpoint = f"/repos/{owner}/{repo}/issues/{pr_number}/comments"
            data = {"body": body}

        result = self._request("POST", endpoint, json=data)
        return str(result["id"])

    def _get_pr_head_commit(self, pr_number: int) -> str:
        """获取 PR 的 head commit SHA"""
        owner, repo = self._parse_repo_url()
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        pr = self._request("GET", endpoint)
        return pr["head"]["sha"]

    def create_review_comments_batch(self, pr_number: int, comments: list[ReviewComment]) -> list[str]:
        """
        批量创建评论

        Args:
            pr_number: PR 编号
            comments: 评论列表

        Returns:
            评论 ID 列表
        """
        comment_ids = []

        # 按 severity 分组，优先处理高 severity
        severity_order = {"error": 0, "warning": 1, "info": 2}
        sorted_comments = sorted(comments, key=lambda c: severity_order.get(c.severity, 3))

        for comment in sorted_comments:
            try:
                cid = self.create_review_comment(
                    pr_number=pr_number,
                    body=comment.body,
                    path=comment.path,
                    line=comment.line
                )
                comment_ids.append(cid)
            except RuntimeError:
                # 忽略失败的评论
                pass

        return comment_ids

    def delete_comment(self, comment_id: str) -> bool:
        """删除评论"""
        owner, repo = self._parse_repo_url()
        endpoint = f"/repos/{owner}/{repo}/comments/{comment_id}"

        try:
            self._request("DELETE", endpoint)
            return True
        except RuntimeError:
            return False
