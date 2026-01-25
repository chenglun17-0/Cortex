"""GitLab Provider 实现"""
from typing import Optional
from urllib.parse import urlparse
from gitlab import Gitlab
from gitlab.exceptions import GitlabGetError, GitlabCreateError, GitlabMRClosedError

from cli.providers.base import GitProvider, PRInfo


class GitLabProvider(GitProvider):
    """GitLab Provider 实现"""

    def __init__(self, token: str, repo_url: str):
        """
        初始化 GitLab Provider

        Args:
            token: GitLab Personal Access Token
            repo_url: 仓库 URL (如 https://gitlab.com/user/repo)
        """
        self.token = token
        self.repo_url = repo_url
        self._client: Gitlab = None
        self._project = None

    def _get_client(self) -> Gitlab:
        """获取 GitLab 客户端"""
        if self._client is None:
            # 提取 base URL
            parsed = urlparse(self.repo_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            self._client = Gitlab(base_url, private_token=self.token)
        return self._client

    def _get_project(self):
        """获取项目对象"""
        if self._project is None:
            # 从 URL 提取 project_id
            parsed = urlparse(self.repo_url)
            path = parsed.path.strip("/")
            self._project = self._get_client().projects.get(path)
        return self._project

    def create_pull_request(
        self,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str = ""
    ) -> PRInfo:
        """
        创建 GitLab Merge Request

        Args:
            title: MR 标题
            source_branch: 源分支
            target_branch: 目标分支
            description: MR 描述

        Returns:
            PRInfo 对象
        """
        project = self._get_project()

        try:
            mr = project.mergerequests.create({
                "source_branch": source_branch,
                "target_branch": target_branch,
                "title": title,
                "description": description
            })

            return PRInfo(
                number=mr.iid,  # GitLab 使用 iid 作为 MR 编号
                title=mr.title,
                url=mr.web_url,
                state=mr.state,
                source_branch=mr.source_branch,
                target_branch=mr.target_branch
            )
        except GitlabCreateError as e:
            error_msg = e.error_message if hasattr(e, 'error_message') else str(e)
            raise RuntimeError(f"Failed to create MR: {error_msg}")

    def get_pull_request(self, mr_iid: int) -> Optional[PRInfo]:
        """获取 MR 信息"""
        project = self._get_project()

        try:
            mr = project.mergerequests.get(mr_iid)
            return PRInfo(
                number=mr.iid,
                title=mr.title,
                url=mr.web_url,
                state=mr.state,
                source_branch=mr.source_branch,
                target_branch=mr.target_branch
            )
        except GitlabGetError:
            return None

    def merge_pull_request(self, mr_iid: int, commit_message: str = "") -> bool:
        """合并 MR"""
        project = self._get_project()

        try:
            mr = project.mergerequests.get(mr_iid)
            mr.merge(commit_message=commit_message or f"Merge branch '{mr.source_branch}' into '{mr.target_branch}'")
            return True
        except GitlabMRClosedError as e:
            raise RuntimeError(f"MR #{mr_iid} is closed and cannot be merged")
        except Exception as e:
            raise RuntimeError(f"Failed to merge MR #{mr_iid}: {str(e)}")

    def get_default_branch(self) -> str:
        """获取默认分支"""
        project = self._get_project()
        return project.default_branch

    def is_mergable(self, mr_iid: int) -> bool:
        """检查 MR 是否可合并"""
        project = self._get_project()

        try:
            mr = project.mergerequests.get(mr_iid)
            return mr.state == "opened" and mr.merge_status in ["can_be_merged", "unchecked"]
        except Exception:
            return False
