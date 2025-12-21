from fastapi import APIRouter, HTTPException
from app.core.security import get_password_hash
from app.models import User as UserModel
from app.schemas.user import UserCreate, User

router = APIRouter()

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    if await UserModel.filter(email=user.email).exists():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)

    user_dict = user.model_dump(exclude={"password"})
    user_dict["hashed_password"] = hashed_pw

    user_obj = await UserModel.create(**user_dict)

    return user_obj