from fastapi import APIRouter
from app.api.v1.endpoints import organizations
api_router = APIRouter()

# 注册路由
api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["organizations"]
)