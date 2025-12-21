from fastapi import APIRouter

from app.api.v1.endpoints import organizations, users, login, tasks, projects
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
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"]
)
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"]
)