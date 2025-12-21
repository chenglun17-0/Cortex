from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.models import User
from app.schemas.token import Token

router = APIRouter()

@router.post("/access-token", response_model=Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    OAuth2 兼容的 Token 登录接口
    CLI 和 Swagger UI 都会发送 username 和 password 到这里
    """
    # 查找用户 (使用 Active Record 风格)
    # 注意：OAuth2 规范里字段名叫 username，但我们实际可能用 email 登录
    # 这里假设用户输入的是 email
    user = await User.filter(email=form_data.username).first()
    # 验证
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # 生成 Token (将用户 ID 放入 Token)
    access_token = security.create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer"
    )