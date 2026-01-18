import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from tortoise import Tortoise

load_dotenv()

def get_db_config():
    """从 .env 读取数据库配置"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL not set in .env")

    parsed = urlparse(database_url)

    credentials = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/"),
    }

    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": credentials,
            },
        },
        "apps": {
            "models": {
                "models": ["app.models"],
                "default_connection": "default",
            },
        },
    }

TORTOISE_ORM = get_db_config()

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
