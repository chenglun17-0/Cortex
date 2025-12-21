from typing import Optional
from pydantic import BaseModel


# 基础字段
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

# 创建时的参数
class ProjectCreate(ProjectBase):
    pass


# 返回给前端的完整数据
class ProjectRead(ProjectBase):
    id: int
    owner_id: Optional[int]
    organization_id: int
    class Config:
        from_attributes = True