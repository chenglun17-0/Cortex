from typing import TYPE_CHECKING
from tortoise import fields, models

if TYPE_CHECKING:
    from .user import User
    from .project import Project

class Organization(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, index=True)

    # 关系
    users: fields.ReverseRelation["User"]
    projects: fields.ReverseRelation["Project"]

    class Meta:
        table = "organizations"
