from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.schemas.task import TaskCreate, TaskRead
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
    获取“分配给当前用户”的所有任务
    CLI 将调用此接口来显示可选任务列表
    """
    tasks = await Task.filter(assignee=current_user).all()
    return tasks