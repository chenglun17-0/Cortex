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
from app.models import Task, User, Project, ProjectMember, TaskComment, TaskCollaborator
from app.services.vector_store import upsert_task_embedding, delete_task_embedding

router = APIRouter()
logger = logging.getLogger(__name__)


async def _is_project_member(project_id: int, user_id: int) -> bool:
    return await ProjectMember.filter(project_id=project_id, user_id=user_id).exists()


async def _get_project_participant_ids(project: Project) -> set[int]:
    participant_ids = set(
        await ProjectMember.filter(project_id=project.id).values_list("user_id", flat=True)
    )
    if project.owner_id:
        participant_ids.add(project.owner_id)
    return participant_ids


def _normalize_collaborator_ids(collaborator_ids: List[int] | None, assignee_id: int | None) -> List[int]:
    if not collaborator_ids:
        return []
    normalized: List[int] = []
    seen: set[int] = set()
    for collaborator_id in collaborator_ids:
        if collaborator_id is None:
            continue
        if assignee_id is not None and collaborator_id == assignee_id:
            continue
        if collaborator_id in seen:
            continue
        seen.add(collaborator_id)
        normalized.append(collaborator_id)
    return normalized


def _ensure_participants_valid(
    participant_ids: set[int],
    assignee_id: int | None,
    collaborator_ids: List[int],
):
    if assignee_id is not None and assignee_id not in participant_ids:
        raise HTTPException(status_code=400, detail="负责人必须是项目成员或项目负责人")

    invalid_collaborators = sorted({uid for uid in collaborator_ids if uid not in participant_ids})
    if invalid_collaborators:
        raise HTTPException(
            status_code=400,
            detail=f"协同人必须是项目成员或项目负责人: {invalid_collaborators}",
        )


async def _replace_task_collaborators(task_id: int, collaborator_ids: List[int]) -> None:
    await TaskCollaborator.filter(task_id=task_id).delete()
    if collaborator_ids:
        await TaskCollaborator.bulk_create(
            [TaskCollaborator(task_id=task_id, user_id=user_id) for user_id in collaborator_ids]
        )


async def _get_task_collaborator_map(task_ids: List[int]) -> dict[int, List[int]]:
    if not task_ids:
        return {}

    collaborator_pairs = await TaskCollaborator.filter(
        task_id__in=task_ids
    ).values_list("task_id", "user_id")

    collaborator_map: dict[int, List[int]] = {}
    for task_id, user_id in collaborator_pairs:
        collaborator_map.setdefault(task_id, []).append(user_id)
    return collaborator_map


def _serialize_task(task: Task, collaborator_ids: List[int]) -> dict:
    task_payload = TaskRead.model_validate(task, from_attributes=True).model_dump()
    task_payload["collaborator_ids"] = collaborator_ids
    return task_payload


async def _serialize_tasks(tasks: List[Task]) -> List[dict]:
    collaborator_map = await _get_task_collaborator_map([task.id for task in tasks])
    return [_serialize_task(task, collaborator_map.get(task.id, [])) for task in tasks]


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

    if await TaskCollaborator.filter(task_id=task.id, user_id=current_user.id).exists():
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

    if await TaskCollaborator.filter(task_id=task.id, user_id=current_user.id).exists():
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

    # 2. 校验负责人和协同人
    assignee_id = task_in.assignee_id if task_in.assignee_id is not None else current_user.id
    collaborator_ids = _normalize_collaborator_ids(task_in.collaborator_ids, assignee_id)
    participant_ids = await _get_project_participant_ids(project)
    _ensure_participants_valid(
        participant_ids=participant_ids,
        assignee_id=assignee_id,
        collaborator_ids=collaborator_ids,
    )

    # 3. 创建任务，自动将当前用户设为 assignee（如果未指定）
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

    # 4. 写入协同人关系
    await _replace_task_collaborators(task.id, collaborator_ids)

    # 5. 存储任务向量（异步，不阻塞响应）
    text_content = f"{task_in.title}\n{task_in.description or ''}"
    await upsert_task_embedding(task.id, text_content)

    return _serialize_task(task, collaborator_ids)


@router.get("/", response_model=List[TaskRead])
async def read_my_tasks(
        current_user: User = Depends(get_current_user)
):
    """
    获取"分配给当前用户"的所有任务（排除已软删除的）
    CLI 将调用此接口来显示可选任务列表
    """
    assigned_task_ids = await Task.filter(
        assignee=current_user,
        deleted_at__isnull=True,
    ).values_list("id", flat=True)
    collaborated_task_ids = await TaskCollaborator.filter(
        user_id=current_user.id
    ).values_list("task_id", flat=True)

    visible_task_ids = sorted(set(assigned_task_ids) | set(collaborated_task_ids))
    if not visible_task_ids:
        return []

    tasks = await Task.filter(
        id__in=visible_task_ids,
        deleted_at__isnull=True,
    ).all()
    return await _serialize_tasks(tasks)

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
    return await _serialize_tasks(tasks)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    获取单个任务详情（已软删除的任务返回 404）
    """
    task = await _ensure_task_access(task_id=task_id, current_user=current_user)
    collaborator_map = await _get_task_collaborator_map([task.id])
    return _serialize_task(task, collaborator_map.get(task.id, []))

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
    update_data = task_update.model_dump(exclude_unset=True)
    collaborator_ids_provided = "collaborator_ids" in update_data
    collaborator_ids_raw = update_data.pop("collaborator_ids", None)
    should_replace_collaborators = "assignee_id" in update_data or collaborator_ids_provided

    if should_replace_collaborators:
        project = await Project.get_or_none(id=task.project_id, deleted_at__isnull=True)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        effective_assignee_id = update_data.get("assignee_id", task.assignee_id)
        if collaborator_ids_provided:
            collaborator_ids = _normalize_collaborator_ids(
                collaborator_ids_raw,
                effective_assignee_id,
            )
        else:
            collaborator_map = await _get_task_collaborator_map([task.id])
            collaborator_ids = _normalize_collaborator_ids(
                collaborator_map.get(task.id, []),
                effective_assignee_id,
            )
        participant_ids = await _get_project_participant_ids(project)
        _ensure_participants_valid(
            participant_ids=participant_ids,
            assignee_id=effective_assignee_id,
            collaborator_ids=collaborator_ids,
        )
    else:
        collaborator_ids = None

    for key, value in update_data.items():
        setattr(task, key, value)

    # 4. 保存
    await task.save()

    if should_replace_collaborators:
        await _replace_task_collaborators(task.id, collaborator_ids)

    # 5. 如果标题或描述更新，同步更新向量
    if "title" in update_data or "description" in update_data:
        text_content = f"{task.title}\n{task.description or ''}"
        await upsert_task_embedding(task.id, text_content)

    if collaborator_ids is None:
        collaborator_map = await _get_task_collaborator_map([task.id])
        collaborator_ids = collaborator_map.get(task.id, [])

    return _serialize_task(task, collaborator_ids)


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
