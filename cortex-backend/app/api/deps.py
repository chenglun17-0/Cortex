from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
import jwt
from app.core import config, security
from app.models import User

# 指向登录接口的 URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        # Token 的 sub 字段存的是 User ID
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    # 从数据库查询用户
    user = await User.get_or_none(id=user_id)
    if user is None:
        raise credentials_exception
    return user
