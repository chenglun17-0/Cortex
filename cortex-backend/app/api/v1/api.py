from fastapi import APIRouter

from app.api.v1.endpoints import organizations, users, login
api_router = APIRouter()

# 注册路由
api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["organizations"]
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)
api_router.include_router(
    login.router,
    prefix="/login",
    tags=["login"]
)