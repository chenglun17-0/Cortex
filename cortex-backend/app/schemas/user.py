from typing import Optional

from sqlmodel import SQLModel

# User 基础类
class UserBase(SQLModel):
    username: str
    email: str
    organization_id: Optional[int] = None

# 创建请求模型：额外包含明文密码
class UserCreate(UserBase):
    password: str

# 读取响应模型：不包含密码，包含 ID
class UserRead(UserBase):
    id: int