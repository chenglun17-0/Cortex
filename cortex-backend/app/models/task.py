from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlmodel import SQLModel, Relationship, Field

if TYPE_CHECKING:
    from .project import Project
    from .user import User

class Task(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key = True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="TODO")
    priority: str = Field(default="MEDIUM")

    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    assignee_id: Optional[int] = Field(default=None, foreign_key="user.id")

    created_at: datetime = Field(default=datetime.now())

    # 关系
    project: Optional["Project"] = Relationship(back_populates="tasks")
    assignee: Optional["User"] = Relationship(back_populates="tasks")