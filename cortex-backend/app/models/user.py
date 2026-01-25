from typing import TYPE_CHECKING, Optional, List

from tortoise import fields, models

if TYPE_CHECKING:
    from .project import Project
    from .task import Task

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True, index=True)
    email = fields.CharField(max_length=100, unique=True, index=True)
    hashed_password = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_login_at = fields.DatetimeField(null=True)
    # 外键：会自动生成 organization_id 字段
    organization = fields.ForeignKeyField(
        "models.Organization", related_name="users", null=True
    )
    organization_id: Optional[int]
    # 创建的项目
    owned_projects: fields.ReverseRelation["Project"]
    # 参与的项目
    joined_projects: fields.ReverseRelation["Project"]
    # 我的任务
    tasks: fields.ReverseRelation["Task"]
    class Meta:
        table = "users"