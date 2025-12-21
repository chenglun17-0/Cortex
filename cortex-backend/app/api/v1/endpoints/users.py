from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.db import get_session
from app.models import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter()

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate):
    if User.where(email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)

    user = User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_pw,
        organization_id = user.organization_id
    )
    return user