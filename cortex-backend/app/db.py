from sqlmodel import create_engine, text, Session
import os
from dotenv import load_dotenv
from typing import Generator
# 读取.env
load_dotenv()
# 获取数据库链接
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")
# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# 测试数据库链接
def test_connection():
    try:
        with Session(engine) as session:
            result = session.exec(text("SELECT 1"))
            print("==============================")
            print("成功连接数据库")
            print(f"测试查询结果：{result.first()}")
            print("==============================")
    except Exception as e:
        print("==============================")
        print("数据库连接失败")
        print(f"错误信息: {e}")
        print("==============================")

if __name__ == "__main__":
    test_connection()