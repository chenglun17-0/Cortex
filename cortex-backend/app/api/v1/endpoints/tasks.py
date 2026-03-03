import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user
from app.schemas.task import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TaskCommentCreate,
    TaskCommentRead,
    TaskCommentListResponse,
)
from app.models import Task, User, Project, ProjectMember, TaskComment
from app.services.vector_store import upsert_task_embedding, delete_task_embedding

router = APIRouter()
logger = logging.getLogger(__name__)


async def _is_project_member(project_id: int, user_id: int) -> bool:
    return await ProjectMember.filter(project_id=project_id, user_id=user_id).exists()


async def _ensure_project_access(project_id: int, current_user: User) -> Project:
    project = await Project.get_or_none(id=project_id, deleted_at__isnull=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id == current_user.id:
        return project

    if await _is_project_member(project_id=project_id, user_id=current_user.id):
        return project

    raise HTTPException(status_code=403, detail="No access to project")


async def _ensure_task_access(task_id: int, current_user: User) -> Task:
    """
    校验任务访问权限：任务 assignee、项目 owner 或项目成员可访问
    """
    task = await Task.get_or_none(id=task_id, deleted_at__isnull=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.assignee_id == current_user.id:
        return task

    project = await Project.get_or_none(id=task.project_id, deleted_at__isnull=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id == current_user.id:
        return task

    if await _is_project_member(project_id=task.project_id, user_id=current_user.id):
        return task

    raise HTTPException(status_code=403, detail="No access to task")


async def _ensure_task_restore_access(task_id: int, current_user: User) -> Task:
    """
    校验恢复任务访问权限：任务需存在（可已软删除），且当前用户有访问权限
    """
    task = await Task.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = await Project.get_or_none(id=task.project_id, deleted_at__isnull=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if task.assignee_id == current_user.id:
        return task

    if project.owner_id == current_user.id:
        return task

    if await _is_project_member(project_id=task.project_id, user_id=current_user.id):
        return task

    raise HTTPException(status_code=403, detail="No access to task")


@router.post("/", response_model=TaskRead)
async def create_task(
        task_in: TaskCreate,
        current_user: User = Depends(get_current_user)  # 确保已登录
):
    # 1. 检查项目存在且当前用户可访问
    project = await _ensure_project_access(project_id=task_in.project_id, current_user=current_user)

    # 2. 创建任务，自动将当前用户设为 assignee（如果未指定）
    assignee_id = task_in.assignee_id or current_user.id
    task = await Task.create(
        title=task_in.title,
        description=task_in.description,
        type=task_in.type,
        priority=task_in.priority,
        status=task_in.status,
        deadline=task_in.deadline,
        project=project,
        assignee_id=assignee_id
    )

    # 3. 存储任务向量（异步，不阻塞响应）
    text_content = f"{task_in.title}\n{task_in.description or ''}"
    await upsert_task_embedding(task.id, text_content)

    return task


@router.get("/", response_model=List[TaskRead])
async def read_my_tasks(
        current_user: User = Depends(get_current_user)
):
    """
    获取"分配给当前用户"的所有任务（排除已软删除的）
    CLI 将调用此接口来显示可选任务列表
    """
    tasks = await Task.filter(assignee=current_user, deleted_at__isnull=True).all()
    return tasks

@router.get("/project/{project_id}", response_model=List[TaskRead])
async def get_project_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    获取项目下所有任务（排除已软删除的）
    :param project_id:
    :param current_user:
    :return:
    """
    await _ensure_project_access(project_id=project_id, current_user=current_user)
    tasks = await Task.filter(project_id=project_id, deleted_at__isnull=True).all()
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    获取单个任务详情（已软删除的任务返回 404）
    """
    task = await _ensure_task_access(task_id=task_id, current_user=current_user)
    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    软删除任务（设置 deleted_at 为当前时间）
    """
    task = await _ensure_task_access(task_id=task_id, current_user=current_user)

    task.deleted_at = datetime.utcnow()
    await task.save()

    # 删除任务向量（异步）
    await delete_task_embedding(task_id)

    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/restore")
async def restore_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    恢复软删除任务（将 deleted_at 重置为 null）
    """
    task = await _ensure_task_restore_access(task_id=task_id, current_user=current_user)

    if task.deleted_at is None:
        raise HTTPException(status_code=400, detail="Task is not deleted")

    task.deleted_at = None
    await task.save()

    # 恢复任务向量
    text_content = f"{task.title}\n{task.description or ''}"
    try:
        await upsert_task_embedding(task.id, text_content)
    except Exception as exc:
        logger.warning("Failed to rebuild embedding after restore (task_id=%s): %s", task.id, exc)

    return {"message": "Task restored successfully"}


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    更新任务状态或详情
    """
    # 1. 查找任务
    task = await _ensure_task_access(task_id=task_id, current_user=current_user)

    # 2. 权限检查 (可选: 只能改自己指派的任务?)
    # if task.assignee_id != current_user.id: ...

    # 3. 更新字段 (exclude_unset=True 确保只更新传进来的字段)
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    # 4. 保存
    await task.save()

    # 5. 如果标题或描述更新，同步更新向量
    if "title" in update_data or "description" in update_data:
        text_content = f"{task.title}\n{task.description or ''}"
        await upsert_task_embedding(task.id, text_content)

    return task


@router.get("/{task_id}/comments", response_model=TaskCommentListResponse)
async def get_task_comments(
    task_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """
    获取任务评论列表（按创建时间倒序，新评论优先）
    """
    await _ensure_task_access(task_id=task_id, current_user=current_user)

    offset = (page - 1) * page_size
    comment_qs = TaskComment.filter(task_id=task_id)
    total = await comment_qs.count()
    comments = (
        await comment_qs
        .order_by("-created_at", "-id")
        .offset(offset)
        .limit(page_size)
        .prefetch_related("author")
        .all()
    )

    return {
        "items": comments,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/{task_id}/comments", response_model=TaskCommentRead)
async def create_task_comment(
    task_id: int,
    comment_in: TaskCommentCreate,
    current_user: User = Depends(get_current_user),
):
    """
    创建任务评论
    """
    await _ensure_task_access(task_id=task_id, current_user=current_user)

    content = comment_in.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")

    comment = await TaskComment.create(
        content=content,
        task_id=task_id,
        author_id=current_user.id,
    )
    await comment.fetch_related("author")
    return comment
