from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# 1. 基础 Schema (Base)
# 包含 User 和 System 共享的字段
# 这里的 max_length=100 对应数据库模型中的 max_length=100
class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=100, description="组织名称")

# 2. 创建 Schema (Create)
# 用于 POST /organizations/ 请求体
# 继承自 Base，如果有额外必填项可以在此添加
class OrganizationCreate(OrganizationBase):
    pass

# 3. 更新 Schema (Update)
# 用于 PATCH /organizations/{id} 请求体
# 所有字段都是 Optional 的，因为用户可能只想修改名称
class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)

# 4. 响应 Schema (Response)
# 用于 API 返回数据 (GET, POST return)
# 包含数据库生成的字段 (如 id)
class Organization(OrganizationBase):
    id: int

    # Pydantic V2 配置：允许从 ORM 对象读取数据
    model_config = ConfigDict(from_attributes=True)

# 5. 包含关系的详细响应 Schema
# 如果你需要返回组织下的用户或项目，可以定义这个
# 注意：这需要 User 和 Project 的 Schema 已经定义，否则会循环引用
# from .user import User
# from .project import Project

class OrganizationDetail(Organization):
    # users: List["User"] = []
    # projects: List["Project"] = []
    pass