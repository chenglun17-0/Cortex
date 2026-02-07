import os
from urllib.parse import urlparse

from dotenv import load_dotenv

# 读取.env
load_dotenv()

# ⚠️ 警告: 生产环境必须设置 SECRET_KEY 环境变量！
# 不要使用代码库中的默认值，避免安全风险
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is not set. "
        "Please set it in your .env file or environment variables."
    )
ALGORITHM = "HS256"
ACCESS__TOKEN_EXPIRE_MINUTES = 60 * 24 * 30 # 30天过期
# 获取数据库链接
DATABASE_URL = os.getenv("DATABASE_URL")

# 解析数据库配置
_db_parsed = urlparse(DATABASE_URL) if DATABASE_URL else None
DB_HOST = _db_parsed.hostname if _db_parsed else None
DB_PORT = _db_parsed.port if _db_parsed else 5432
DB_USER = _db_parsed.username if _db_parsed else None
DB_PASSWORD = _db_parsed.password if _db_parsed else None
DB_NAME = _db_parsed.path.lstrip("/") if _db_parsed else None