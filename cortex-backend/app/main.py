from fastapi import FastAPI, Request
from sqlmodel import Session

from app.api.v1.api import api_router
from app.core.context import set_db_session
from app.db import engine

app = FastAPI(title="Cortex Project Manager",
              openapi_url="/api/v1/openapi.json"
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # 1. 请求开始：创建 Session
    with Session(engine) as session:
        # 2. 将 Session 放入全局上下文
        set_db_session(session)
        # 3. 处理请求 (进入路由函数)
        response = await call_next(request)
        # 4. 请求结束：自动关闭 Session (with 语句会自动处理 close)
        return response

@app.get("/")
def get_root():
    return {"message": "Cortex API is running!"}

app.include_router(api_router, prefix="/api/v1")