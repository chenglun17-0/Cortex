"""
相似度检索 API 端点

提供任务语义相似度搜索功能：
- POST /similarity/search - 搜索相似任务
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.vector_store import search_similar_tasks
from app.schemas.similarity import (
    SimilaritySearchRequest,
    SimilaritySearchResponse,
    SimilarTaskItem,
)
from app.api.deps import get_current_user


router = APIRouter(prefix="/similarity", tags=["similarity"])


class SimilaritySearchBody(BaseModel):
    """相似度搜索请求体（兼容非 Pydantic 的调用）"""
    text: str
    exclude_task_id: Optional[int] = None
    limit: int = 5
    threshold: float = 0.5


@router.post("/search", response_model=SimilaritySearchResponse)
async def search_similar(
    request: SimilaritySearchRequest,
    current_user=Depends(get_current_user),
):
    """
    搜索相似任务

    - 根据输入的文本内容，在已有任务中搜索语义相似的任务
    - 返回相似度超过阈值的结果，按相似度降序排列
    """
    try:
        results = await search_similar_tasks(
            text_content=request.text,
            exclude_task_id=request.exclude_task_id,
            limit=request.limit,
            threshold=request.threshold,
        )

        return SimilaritySearchResponse(
            success=True,
            query=request.text,
            results=[
                SimilarTaskItem(
                    task_id=r["task_id"],
                    title=r["title"],
                    description=r["description"],
                    status=r["status"],
                    priority=r["priority"],
                    project_id=r["project_id"],
                    similarity=r["similarity"],
                    created_at=r["created_at"],
                )
                for r in results
            ],
            total=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "similarity"}
