from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.security import get_password_hash, verify_password
from app.models import User as UserModel
from app.schemas.user import UserCreate, User, UserUpdateProfile
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdateProfile,
    current_user: UserModel = Depends(get_current_user)
):
    """
    更新当前登录用户信息
    """
    if user_in.password:
        if not user_in.old_password:
             raise HTTPException(status_code=400, detail="修改密码需要提供旧密码")
        if not verify_password(user_in.old_password, current_user.hashed_password):
             raise HTTPException(status_code=400, detail="旧密码错误")
        current_user.hashed_password = get_password_hash(user_in.password)

    if user_in.username:
        # Check if username already exists (excluding current user)
        if await UserModel.filter(username=user_in.username).exclude(id=current_user.id).exists():
             raise HTTPException(status_code=400, detail="用户名已被使用")
        current_user.username = user_in.username

    await current_user.save()
    return current_user

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    if await UserModel.filter(email=user.email).exists():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)

    user_dict = user.model_dump(exclude={"password"})
    user_dict["hashed_password"] = hashed_pw

    user_obj = await UserModel.create(**user_dict)

    return user_obj

@router.get("/search", response_model=List[User])
async def search_users(
    q: str = Query("", description="搜索关键字（可为空）"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    按用户名搜索用户（默认返回当前组织下前 20 个可添加成员）
    """
    query_text = q.strip()

    users_qs = UserModel.filter(organization_id=current_user.organization_id)
    if query_text:
        users_qs = users_qs.filter(username__icontains=query_text)

    users = await users_qs.exclude(id=current_user.id).limit(20).all()
    return users
