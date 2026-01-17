from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

# 基础字段
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    status: str = "TODO"
    deadline: Optional[date] = None

# 创建任务时的参数
class TaskCreate(TaskBase):
    project_id: int
    assignee_id: Optional[int] = None

# 更新任务时的参数 (所有字段都是可选的)
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    branch_name: Optional[str] = None
    deadline: Optional[date] = None

# 返回给前端/CLI 的完整数据
class TaskRead(TaskBase):
    id: int
    project_id: int
    branch_name: Optional[str] = None
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True