from datetime import datetime, timedelta
from typing import Union, Any

import jwt
from passlib.context import CryptContext

from app.core import config

# 定义哈希上下文，使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码的哈希值"""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any]) -> str:
    """生成 JWT 访问令牌"""
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS__TOKEN_EXPIRE_MINUTES)
    # subject 一般存放用户 id
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt