from typing import Optional
from tortoise import fields, models

class ProjectMember(models.Model):
    id = fields.IntField(pk=True)
    # 关联到 Project
    project = fields.ForeignKeyField(
        "models.Project",
        related_name="memberships"  # 方便反向查询: project.memberships
    )

    # 关联到 User
    user = fields.ForeignKeyField(
        "models.User",
        related_name="memberships"
    )
    # 记录加入时间 (自动生成)
    joined_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "project_members"  # 必须与 Project 模型中 through="..." 一致
        unique_together = (("project", "user"),)  # 防止重复加入同一个项目