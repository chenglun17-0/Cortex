from typing import Optional, List
from pydantic import BaseModel


# 基础字段
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

# 创建时的参数
class ProjectCreate(ProjectBase):
    pass

# 更新项目时的参数
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# 成员信息
class ProjectMemberResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

# 返回给前端的完整数据
class ProjectRead(ProjectBase):
    id: int
    owner_id: Optional[int]
    organization_id: int
    members: List[ProjectMemberResponse] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True