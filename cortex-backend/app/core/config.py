import os

from dotenv import load_dotenv

# 读取.env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "Superman")
ALGORITHM = "HS256"
ACCESS__TOKEN_EXPIRE_MINUTES = 60 * 24 * 30 # 30天过期
# 获取数据库链接
DATABASE_URL = os.getenv("DATABASE_URL")