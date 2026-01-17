from tortoise import fields, models

class Task(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)

    status = fields.CharField(max_length=20, default="TODO", index=True)
    priority = fields.CharField(max_length=20, default="MEDIUM")
    branch_name = fields.CharField(max_length=255, null=True, index=True)
    deadline = fields.DateField(null=True)
    # 外键关系
    project = fields.ForeignKeyField(
        "models.Project",
        related_name="tasks"  # project.tasks 可获取所有任务
    )

    assignee = fields.ForeignKeyField(
        "models.User",
        related_name="assigned_tasks",  # user.assigned_tasks 可获取指派给他的任务
        null=True  # 任务刚创建时可能没人认领
    )

    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)  # 每次保存自动更新

    class Meta:
        table = "tasks"
        ordering = ["-created_at"]  # 默认按创建时间倒序排列