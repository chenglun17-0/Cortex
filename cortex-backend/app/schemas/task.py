from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# 基础字段
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    status: str = "TODO"

# 创建任务时的参数
class TaskCreate(TaskBase):
    project_id: int
    assignee_id: Optional[int] = None

# 返回给前端/CLI 的完整数据
class TaskRead(TaskBase):
    id: int
    project_id: int
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True