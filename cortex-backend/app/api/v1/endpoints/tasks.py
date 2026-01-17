from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.models import Task, User, Project

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

    # 2. 创建任务
    task = await Task.create(**task_in.dict())
    return task


@router.get("/", response_model=List[TaskRead])
async def read_my_tasks(
        current_user: User = Depends(get_current_user)
):
    """
    获取"分配给当前用户"的所有任务
    CLI 将调用此接口来显示可选任务列表
    """
    tasks = await Task.filter(assignee=current_user).all()
    return tasks

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    获取单个任务详情
    """
    task = await Task.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/project/{project_id}", response_model=List[TaskRead])
async def get_project_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    获取项目下所有任务
    :param project_id:
    :param current_user:
    :return:
    """
    tasks = await Task.filter(project_id=project_id).all()
    return tasks


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
    return task
