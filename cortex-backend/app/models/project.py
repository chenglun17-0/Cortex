from datetime import datetime
from tortoise import fields, models

class Project(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, index=True)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    # 软删除标记
    deleted_at = fields.DatetimeField(null=True)

    organization = fields.ForeignKeyField(
        "models.Organization", related_name="projects", null=True
    )

    # 项目负责人
    owner = fields.ForeignKeyField(
        "models.User", related_name="owned_projects", null=True
    )

    # 多对多：项目成员
    # Tortoise 支持通过 through 指定中间表，这对应 ProjectMember
    members = fields.ManyToManyField(
        "models.User",
        related_name="joined_projects",
        through="project_members",
        forward_key="project_id",
        backward_key="user_id"
    )

    class Meta:
        table = "projects"
