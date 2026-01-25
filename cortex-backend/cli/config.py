import json
from pathlib import Path
from typing import Optional, Dict, Any
import typer

# 定义配置文件路径: ~/.cortex/config.json
APP_NAME = "cortex"
CONFIG_DIR = Path.home() / f".{APP_NAME}"
CONFIG_FILE = CONFIG_DIR / "config.json"

"""配置键"""
# 后端 API 地址
API_URL = "url"
GIT_MAIN_BRANCH = "git_main_branch"
ACCESS_TOKEN = "access_token"
DELETE_LOCAL_ON_DONE = "delete_local_on_done"
DELETE_REMOTE_ON_DONE = "delete_remote_on_done"

# Git Provider 配置
GIT_PROVIDER = "git_provider"  # "github" 或 "gitlab"
GITHUB_TOKEN = "github_token"
GITLAB_TOKEN = "gitlab_token"

# AI 配置
AI_PROVIDER = "ai_provider"  # "openai", "anthropic", "local"
AI_API_KEY = "ai_api_key"
AI_MODEL = "ai_model"
AI_BASE_URL = "ai_base_url"  # 用于本地模型

# AI 代码审查配置
AI_REVIEW_ENABLED = "ai_review_enabled"
AI_REVIEW_DIMENSIONS = "ai_review_dimensions"  # ["quality", "security", "type", "convention"]

def _load_full_config() -> Dict[str, Any]:
    """读取完整配置"""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def _save_full_config(data: Dict[str, Any]):
    """保存完整配置"""
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_config_value(key: str, default: Any = None) -> Any:
    data = _load_full_config()
    return data.get(key, default)

def set_config_value(key: str, value: Any):
    data = _load_full_config()
    data[key] = value
    _save_full_config(data)
