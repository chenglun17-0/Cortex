from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from .base import ActiveModel

if TYPE_CHECKING:
    from .user import User
    from .project import Project

class Organization(ActiveModel, table=True):
    id: Optional[int] = Field(default=None, primary_key = True)
    name: str = Field(index = True)

    # 关系
    users: List["User"] = Relationship(back_populates="organization")
    projects: List["Project"] = Relationship(back_populates="organization")