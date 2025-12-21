from fastapi import FastAPI
from app.api.v1.api import api_router
app = FastAPI(title="Cortex Project Manager",
              openapi_url="/api/v1/openapi.json"
)

@app.get("/")
def get_root():
    return {"message": "Cortex API is running!"}

app.include_router(api_router, prefix="/api/v1")