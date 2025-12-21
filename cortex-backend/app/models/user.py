from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, SQLModel, Relationship
from .project_member import ProjectMember

if TYPE_CHECKING:
    from .organization import Organization
    from .project import Project
    from .task import Task

class User(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key = True)
    username: str = Field(index = True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    organization_id: Optional[int] = Field(default=None, foreign_key="organization.id")

    # 关系: 所属组织
    organization: Optional["Organization"] = Relationship(back_populates="users")

    # 关系: 创建的项目
    owned_projects: List["Project"] = Relationship(back_populates="owner")

    # 关系: 参与的项目
    joined_projects: List["Project"] = Relationship(
        back_populates="members",link_model=ProjectMember
    )

    # 关系: 我的任务
    tasks: List["Task"] = Relationship(back_populates="assignee")