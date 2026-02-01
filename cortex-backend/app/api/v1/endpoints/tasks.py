from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.models import Task, User, Project
from app.services.vector_store import upsert_task_embedding, delete_task_embedding

router = APIRouter()


@router.post("/", response_model=TaskRead)
async def create_task(
        task_in: TaskCreate,
        current_user: User = Depends(get_current_user)  # 确保已登录
):
    # 1. 检查项目是否存在
    project = await Project.get_or_none(id=task_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

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

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    获取单个任务详情（已软删除的任务返回 404）
    """
    task = await Task.get_or_none(id=task_id, deleted_at__isnull=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

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
    tasks = await Task.filter(project_id=project_id, deleted_at__isnull=True).all()
    return tasks


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    软删除任务（设置 deleted_at 为当前时间）
    """
    task = await Task.get_or_none(id=task_id, deleted_at__isnull=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.deleted_at = datetime.utcnow()
    await task.save()

    # 删除任务向量（异步）
    await delete_task_embedding(task_id)

    return {"message": "Task deleted successfully"}


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
    task = await Task.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. 权限检查 (可选: 只能改自己指派的任务?)
    # if task.assignee_id != current_user.id: ...

    # 3. 更新字段 (exclude_unset=True 确保只更新传进来的字段)
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    # 4. 保存
    await task.save()

    # 5. 如果标题或描述更新，同步更新向量
    if task_update.title or task_update.description:
        text_content = f"{task.title}\n{task.description or ''}"
        await upsert_task_embedding(task.id, text_content)

    return task
