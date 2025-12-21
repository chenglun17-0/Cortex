from typing import Optional
from pydantic import BaseModel

# 用于响应登录接口 (Response)
class Token(BaseModel):
    access_token: str
    token_type: str

# 用于解析 Token 内容 (Internal Use)
class TokenPayload(BaseModel):
    # JWT 标准中 sub (Subject) 通常存放唯一标识，这里存放用户 ID
    sub: Optional[int] = None