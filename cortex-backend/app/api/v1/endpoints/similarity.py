"""
相似度检索 API 端点

提供任务语义相似度搜索功能：
- POST /similarity/search - 搜索相似任务
"""
import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from app.services.vector_store import search_similar_tasks
from app.schemas.similarity import (
    SimilaritySearchRequest,
    SimilaritySearchResponse,
    SimilarTaskItem,
)
from app.models import TaskComment
from app.api.deps import get_current_user

router = APIRouter(prefix="/similarity", tags=["similarity"])
logger = logging.getLogger(__name__)


def _normalize_text(value: str, max_length: int = 120) -> str:
    text = " ".join(value.split())
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


async def _build_recommendation(task_id: int, description: Optional[str]) -> Optional[str]:
    segments: list[str] = []

    if description and description.strip():
        segments.append(_normalize_text(description, max_length=140))

    comments = (
        await TaskComment.filter(task_id=task_id)
        .order_by("-created_at", "-id")
        .limit(2)
        .all()
    )
    for comment in comments:
        if comment.content and comment.content.strip():
            segments.append(_normalize_text(comment.content, max_length=100))

    if not segments:
        return None

    return " / ".join(segments)


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

        recommendations = await asyncio.gather(
            *[
                _build_recommendation(
                    task_id=r["task_id"],
                    description=r.get("description"),
                )
                for r in results
            ],
            return_exceptions=True,
        )

        safe_recommendations = []
        for recommendation in recommendations:
            if isinstance(recommendation, Exception):
                logger.warning("Failed to build recommendation: %s", recommendation)
                safe_recommendations.append(None)
            else:
                safe_recommendations.append(recommendation)

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
                    recommendation=safe_recommendations[idx],
                )
                for idx, r in enumerate(results)
            ],
            total=len(results),
        )
    except RuntimeError as e:
        # embedding 生成失败
        raise HTTPException(status_code=503, detail=f"AI 服务暂时不可用: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "similarity"}
