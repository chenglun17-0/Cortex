from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# 1. 基础 Schema (Base)
# 包含所有变体共享的字段
class UserBase(BaseModel):
    username: str = Field(..., max_length=50, description="用户名")
    email: EmailStr = Field(..., max_length=100, description="电子邮箱")

    # 提示：EmailStr 需要安装 pydantic[email] 扩展
    # 如果没安装，可以使用 str 类型代替


# 2. 创建 Schema (Create)
# 用于用户注册或管理员创建用户
# 包含原始密码字段
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="原始密码")
    organization_id: Optional[int] = Field(None, description="所属组织ID")


# 3. 更新 Schema (Update)
# 所有字段可选
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=6, description="如果提供则重置密码")
    organization_id: Optional[int] = None


class UserUpdateProfile(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    old_password: Optional[str] = Field(None, description="修改密码时必须提供旧密码")
    password: Optional[str] = Field(None, min_length=6, description="新密码")


# 4. 响应 Schema (Response/Public)
# 用于 API 返回用户信息
# ！！！严禁包含 password 或 hashed_password ！！！
class User(UserBase):
    id: int
    organization_id: Optional[int] = None

    # Pydantic V2 配置：允许从 ORM 对象读取数据
    model_config = ConfigDict(from_attributes=True)


# 5. (内部使用) 数据库 Schema
# 如果某些内部逻辑需要读取哈希密码，可以使用这个，但不要在 API Router 中返回它
class UserInDB(User):
    hashed_password: str