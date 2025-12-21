import json
from pathlib import Path
from typing import Optional
import typer

# 定义配置文件路径: ~/.cortex/config.json
APP_NAME = "cortex"
CONFIG_DIR = Path.home() / f".{APP_NAME}"
CONFIG_FILE = CONFIG_DIR / "config.json"
# 后端 API 地址
API_URL = "http://127.0.0.1:8000/api/v1"

def save_token(token: str):
    """将 Token 保存到本地文件"""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)

    config_data = {"access_token": token}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f)


def get_token() -> Optional[str]:
    """读取本地 Token"""
    if not CONFIG_FILE.exists():
        return None

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("access_token")
    except json.JSONDecodeError:
        return None


def delete_token():
    """注销/删除 Token"""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()