from typing import TYPE_CHECKING, Optional, List

from sqlmodel import SQLModel, Field, Relationship

from .project_member import ProjectMember
if TYPE_CHECKING:
    from .organization import Organization
    from .user import User
    from .task import Task

class Project(SQLModel, table = True):
    id: Optional[ int] = Field(default=None, primary_key = True)
    name: str = Field(index = True)
    description: Optional[str] = None

    organization_id: Optional[int] = Field(default=None, foreign_key="organization.id")
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # 关系
    organization: Optional["Organization"] = Relationship(back_populates="projects")

    # 关系：项目负责人
    owner: Optional["User"] = Relationship(back_populates="owned_projects")

    # 关系：项目成员
    members: List["User"] = Relationship(
        back_populates="joined_projects", link_model=ProjectMember
    )

    tasks: List["Task"] = Relationship(back_populates="project")