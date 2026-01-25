"""
AI Service Module

提供 AI 驱动的文档生成功能：
- Commit Message 生成（遵循 Conventional Commits 规范）
- PR Description 生成
"""
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from openai import OpenAI as OpenAIClient
from anthropic import Anthropic as AnthropicClient

from cli.config import (
    get_config_value,
    AI_PROVIDER,
    AI_API_KEY,
    AI_MODEL,
    AI_BASE_URL,
)


# ============== Prompt Templates ==============

COMMIT_MESSAGE_PROMPT = """你是一个代码提交助手。请根据以下 git diff 生成一个简洁的 commit message。

## 要求：
1. 遵循 Conventional Commits 规范：`<type>: <description>`
2. type 必须是以下之一：feat, fix, docs, style, refactor, test, chore
3. description 简短描述（不超过 72 字符）
4. 如果包含多个相关改动，用一句话概括主要变更

## Git Diff:
{diff}

## 任务标题（供参考）：
{task_title}

请直接输出 commit message，不要包含任何解释或其他内容。"""


PR_DESCRIPTION_PROMPT = """你是一个 PR 描述生成助手。请根据以下信息生成一个完整的 PR 描述。

## Git Diff:
{diff}

## 任务信息：
- 标题：{task_title}
- 类型：{task_type}
- 描述：{task_description}

## 要求：
1. 包含变更摘要（2-3 行简述主要改动）
2. 列出关键变更点（使用 bullet points）
3. 包含测试说明（如果有测试改动）
4. 包含相关任务或 Issue 链接（格式：Task #{task_id}）

请用 Markdown 格式输出。"""


# ============== Abstract Base Class ==============

class AIService(ABC):
    """AI 服务基类"""

    @abstractmethod
    def generate_commit_message(self, diff: str, task_title: str) -> str:
        """生成 commit message"""
        pass

    @abstractmethod
    def generate_pr_description(
        self,
        diff: str,
        task_id: int,
        task_title: str,
        task_type: str,
        task_description: str,
    ) -> str:
        """生成 PR 描述"""
        pass


# ============== Concrete Implementations ==============

class OpenAIService(AIService):
    """OpenAI API 服务"""

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        self.client = OpenAIClient(api_key=api_key, base_url=base_url)
        self.model = model

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content or ""

    def generate_commit_message(self, diff: str, task_title: str) -> str:
        user_prompt = COMMIT_MESSAGE_PROMPT.format(diff=diff, task_title=task_title)
        return self._call_llm("You are a helpful commit message generator.", user_prompt).strip()

    def generate_pr_description(
        self,
        diff: str,
        task_id: int,
        task_title: str,
        task_type: str,
        task_description: str,
    ) -> str:
        user_prompt = PR_DESCRIPTION_PROMPT.format(
            diff=diff,
            task_title=task_title,
            task_type=task_type,
            task_description=task_description,
            task_id=task_id,
        )
        return self._call_llm(
            "You are a helpful PR description generator.",
            user_prompt,
        ).strip()


class AnthropicService(AIService):
    """Anthropic Claude API 服务"""

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        self.client = AnthropicClient(api_key=api_key, base_url=base_url)
        self.model = model

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text if response.content else ""

    def generate_commit_message(self, diff: str, task_title: str) -> str:
        user_prompt = COMMIT_MESSAGE_PROMPT.format(diff=diff, task_title=task_title)
        return self._call_llm(
            "You are a helpful commit message generator.",
            user_prompt,
        ).strip()

    def generate_pr_description(
        self,
        diff: str,
        task_id: int,
        task_title: str,
        task_type: str,
        task_description: str,
    ) -> str:
        user_prompt = PR_DESCRIPTION_PROMPT.format(
            diff=diff,
            task_title=task_title,
            task_type=task_type,
            task_description=task_description,
            task_id=task_id,
        )
        return self._call_llm(
            "You are a helpful PR description generator.",
            user_prompt,
        ).strip()


class LocalModelService(AIService):
    """本地模型服务（如 Ollama, LM Studio 等）"""

    def __init__(self, base_url: str, model: str):
        # 兼容 OpenAI 格式的本地模型 API
        self.client = OpenAIClient(base_url=base_url, api_key="not-needed")
        self.model = model

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用本地 LLM"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content or ""

    def generate_commit_message(self, diff: str, task_title: str) -> str:
        user_prompt = COMMIT_MESSAGE_PROMPT.format(diff=diff, task_title=task_title)
        return self._call_llm(
            "You are a helpful commit message generator.",
            user_prompt,
        ).strip()

    def generate_pr_description(
        self,
        diff: str,
        task_id: int,
        task_title: str,
        task_type: str,
        task_description: str,
    ) -> str:
        user_prompt = PR_DESCRIPTION_PROMPT.format(
            diff=diff,
            task_title=task_title,
            task_type=task_type,
            task_description=task_description,
            task_id=task_id,
        )
        return self._call_llm(
            "You are a helpful PR description generator.",
            user_prompt,
        ).strip()


# ============== Factory Function ==============

def get_ai_service(provider: Optional[str] = None) -> Optional[AIService]:
    """
    获取 AI 服务实例

    Args:
        provider: 提供商名称，如果为 None 则从配置读取

    Returns:
        AI 服务实例，如果配置不完整则返回 None
    """
    if provider is None:
        provider = get_config_value(AI_PROVIDER)

    if not provider:
        return None

    api_key = get_config_value(AI_API_KEY)
    if not api_key:
        return None

    model = get_config_value(AI_MODEL)
    base_url = get_config_value(AI_BASE_URL)

    provider = provider.lower()

    if provider == "openai":
        return OpenAIService(api_key=api_key, model=model or "gpt-4o", base_url=base_url)
    elif provider == "anthropic":
        return AnthropicService(api_key=api_key, model=model or "claude-sonnet-4-20250514", base_url=base_url)
    elif provider == "local":
        if not base_url:
            return None
        return LocalModelService(base_url=base_url, model=model or "llama3")

    return None


# ============== Convenience Functions ==============

def generate_commit_message(diff: str, task_title: str) -> Optional[str]:
    """
    生成 commit message

    Args:
        diff: git diff 内容
        task_title: 任务标题

    Returns:
        生成的 commit message，失败返回 None
    """
    service = get_ai_service()
    if not service:
        return None

    try:
        return service.generate_commit_message(diff, task_title)
    except Exception:
        return None


def generate_pr_description(
    diff: str,
    task_id: int,
    task_title: str,
    task_type: str,
    task_description: str,
) -> str:
    """
    生成 PR 描述

    Args:
        diff: git diff 内容
        task_id: 任务 ID
        task_title: 任务标题
        task_type: 任务类型
        task_description: 任务描述

    Returns:
        生成的 PR 描述
    """
    service = get_ai_service()
    if not service:
        # 返回默认描述
        return f"Task #{task_id}\n\n{task_description}"

    try:
        return service.generate_pr_description(
            diff=diff,
            task_id=task_id,
            task_title=task_title,
            task_type=task_type,
            task_description=task_description,
        )
    except Exception:
        return f"Task #{task_id}\n\n{task_description}"
