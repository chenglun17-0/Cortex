"""
相似度检索 API Schema
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.task import TaskPriority, TaskStatus


class SimilaritySearchRequest(BaseModel):
    """相似度搜索请求"""
    text: str = Field(..., description="查询文本（任务标题或描述）", min_length=1, max_length=1000)
    exclude_task_id: Optional[int] = Field(None, description="排除的任务 ID（创建新任务时传入）")
    limit: int = Field(default=5, ge=1, le=20, description="返回结果数量")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="相似度阈值")


class SimilarTaskItem(BaseModel):
    """相似任务项"""
    task_id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    project_id: int
    similarity: float = Field(..., description="相似度 (0-1)")
    created_at: Optional[str] = None


class SimilaritySearchResponse(BaseModel):
    """相似度搜索响应"""
    success: bool
    query: str
    results: List[SimilarTaskItem]
    total: int
    message: Optional[str] = None
