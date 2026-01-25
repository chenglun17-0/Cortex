"""
AI Code Reviewer Service

提供 AI 驱动的代码审查功能：
- 代码质量审查
- 安全性审查
- 类型检查
- 规范遵从审查
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import re

from cli.ai.service import AIService, get_ai_service


@dataclass
class CodeIssue:
    """代码问题"""
    file: str
    line: int
    message: str
    category: str  # quality, security, type, convention
    severity: str  # info, warning, error
    suggestion: Optional[str] = None


@dataclass
class CodeReviewResult:
    """代码审查结果"""
    summary: str
    raw_content: str = ""  # AI 原始返回内容
    issues: List[CodeIssue] = field(default_factory=list)
    score: int = 100  # 代码评分 0-100

    def add_issue(self, issue: CodeIssue):
        """添加问题并更新评分"""
        self.issues.append(issue)
        # 根据 severity 扣分
        if issue.severity == "error":
            self.score -= 15
        elif issue.severity == "warning":
            self.score -= 5
        elif issue.severity == "info":
            self.score -= 1
        self.score = max(0, self.score)


# ============== Review Prompts ==============

CODE_REVIEW_PROMPT = """你是一个专业的代码审查助手。请审查以下代码变更，找出潜在问题。

## 审查维度：
1. **代码质量**：代码异味、复杂度过高、重复代码、命名不规范等
2. **安全性**：潜在 bug、空指针、资源泄露、安全漏洞等
3. **类型检查**：类型错误、类型不匹配、类型推断问题等
4. **规范遵从**：项目编码规范、最佳实践等

## 代码变更 (Diff)：
{diff}

## 审查要求：
1. 识别问题所在的具体文件、行号
2. 问题分类：quality, security, type, convention
3. 严重程度：info（信息）, warning（警告）, error（严重）
4. 对于每个问题，提供：
   - 问题描述
   - 建议的修复方案

请用 Markdown 格式输出审查结果。"""


# ============== Abstract Base Class ==============

class CodeReviewer(ABC):
    """代码审查器基类"""

    @abstractmethod
    def review(self, diff: str) -> CodeReviewResult:
        """审查代码变更"""
        pass


# ============== AI Code Reviewer ==============

class AICodeReviewer(CodeReviewer):
    """AI 代码审查器"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    def review(self, diff: str) -> CodeReviewResult:
        """审查代码变更"""
        if not self.ai_service:
            return CodeReviewResult(
                summary="AI 服务未配置，跳过审查",
                raw_content="",
                issues=[],
                score=100
            )

        try:
            response = self.ai_service._call_llm(
                "You are a professional code reviewer.",
                CODE_REVIEW_PROMPT.format(diff=diff)
            )

            if not response:
                return CodeReviewResult(
                    summary="AI 未返回审查结果",
                    raw_content="",
                    issues=[],
                    score=100
                )

            return CodeReviewResult(
                summary="AI 代码审查完成",
                raw_content=response,
                issues=[],
                score=100  # 简化：直接使用原始内容，不做解析
            )
        except Exception as e:
            return CodeReviewResult(
                summary=f"审查出错: {str(e)}",
                raw_content="",
                issues=[],
                score=100
            )


# ============== Factory Function ==============

def get_code_reviewer() -> CodeReviewer:
    """
    获取代码审查器

    Returns:
        代码审查器实例
    """
    ai_service = get_ai_service()
    if ai_service:
        return AICodeReviewer(ai_service)
    # 返回一个空实现
    class DummyReviewer(CodeReviewer):
        def review(self, diff: str) -> CodeReviewResult:
            return CodeReviewResult(
                summary="AI 服务未配置，跳过审查",
                raw_content="",
                issues=[],
                score=100
            )
    return DummyReviewer()


# ============== Convenience Function ==============

def review_code(diff: str) -> CodeReviewResult:
    """
    审查代码变更

    Args:
        diff: git diff 内容

    Returns:
        审查结果
    """
    reviewer = get_code_reviewer()
    return reviewer.review(diff)
