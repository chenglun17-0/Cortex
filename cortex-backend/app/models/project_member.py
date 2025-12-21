from typing import Optional

from sqlmodel import SQLModel, Field

from app.models.base import ActiveModel


class ProjectMember(ActiveModel, table=True):
    project_id: Optional[int] = Field(
        default=None, foreign_key="project.id", primary_key=True
    )
    user_id: Optional[ int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )