from fastapi import FastAPI, Request
from app.api.v1.api import api_router
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import DATABASE_URL

app = FastAPI(title="Cortex Project Manager",
              openapi_url="/api/v1/openapi.json"
)
register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["app.models"]}, # 指向模型所在位置
    generate_schemas=True, # 开发阶段设为 True，重启服务自动建表！(类似 Base.metadata.create_all)
    add_exception_handlers=True,
)
@app.get("/")
def get_root():
    return {"message": "Cortex API is running!"}

app.include_router(api_router, prefix="/api/v1")