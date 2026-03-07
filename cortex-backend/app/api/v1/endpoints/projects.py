from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from tortoise.expressions import Q
from app.schemas.project import (
    ProjectCreate, ProjectRead, ProjectUpdate, ProjectMemberResponse
)
from app.models import Project, ProjectMember, User, Task
from app.api.deps import get_current_user

router = APIRouter()


async def get_project_by_id(project_id: int) -> Optional[Project]:
    """获取项目，不包含已删除的"""
    project = await Project.filter(id=project_id, deleted_at__isnull=True).first()
    return project


async def _get_project_members(project: Project) -> list:
    """获取项目的成员列表（内部函数）"""
    memberships = await ProjectMember.filter(project=project).prefetch_related("user")
    return [m.user for m in memberships]


def format_project_response(project: Project, members: list) -> dict:
    """格式化项目返回数据"""
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "owner_id": project.owner_id,
        "organization_id": project.organization_id,
        "members": members,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }


@router.post("/", response_model=ProjectRead)
async def create_project(
        project_in: ProjectCreate,
        current_user: User = Depends(get_current_user)
):
    # 1. 自动获取当前用户的组织 ID
    # TortoiseORM 中，Foreign Key 字段会自动生成一个 _id 后缀的属性
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400,
            detail="You must belong to an organization to create a project."
        )

    # 2. 创建项目
    # 直接使用 organization_id 参数，不需要再查一次 Organization 表
    project = await Project.create(
        name=project_in.name,
        description=project_in.description,
        organization_id=current_user.organization_id,  # 👈 核心修改
        owner=current_user
    )

    # 3. 自动将创建者加入项目成员
    await ProjectMember.create(
        project=project,
        user=current_user
    )

    members = await _get_project_members(project)
    return format_project_response(project, members)


@router.get("/", response_model=List[ProjectRead])
async def read_my_projects(
        current_user: User = Depends(get_current_user)
):
    # 查询我可见的所有项目（负责人或成员，不包含已删除的）
    projects = await Project.filter(
        Q(owner_id=current_user.id) | Q(members__id=current_user.id),
        deleted_at__isnull=True
    ).distinct().all()

    # 格式化返回数据
    result = []
    for project in projects:
        members = await _get_project_members(project)
        result.append(format_project_response(project, members))

    return result


@router.get("/{project_id}", response_model=ProjectRead)
async def read_project(
        project_id: int,
        current_user: User = Depends(get_current_user)
):
    """获取项目详情，包含成员列表"""
    project = await get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    members = await _get_project_members(project)
    return format_project_response(project, members)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
        project_id: int,
        project_in: ProjectUpdate,
        current_user: User = Depends(get_current_user)
):
    """更新项目信息"""
    project = await get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 更新字段
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    await project.save()

    members = await _get_project_members(project)
    return format_project_response(project, members)


@router.delete("/{project_id}")
async def delete_project(
        project_id: int,
        current_user: User = Depends(get_current_user)
):
    """软删除项目"""
    project = await get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 检查是否有未完成的任务
    pending_tasks = await Task.filter(
        project=project,
        deleted_at__isnull=True
    ).count()
    if pending_tasks > 0:
        raise HTTPException(
            status_code=400,
            detail="该项目下还有未完成的任务"
        )

    # 软删除
    project.deleted_at = datetime.utcnow()
    await project.save()

    return {"message": "项目已删除"}


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def get_project_members(
        project_id: int,
        current_user: User = Depends(get_current_user)
):
    """获取项目成员列表"""
    project = await get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    memberships = await ProjectMember.filter(project=project).prefetch_related("user")
    return [m.user for m in memberships]


@router.post("/{project_id}/members")
async def add_project_member(
        project_id: int,
        user_id: int = Query(..., description="要添加的用户ID"),
        current_user: User = Depends(get_current_user)
):
    """添加项目成员"""
    project = await get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 检查用户是否存在
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查是否已是成员
    existing = await ProjectMember.get_or_none(project=project, user=user)
    if existing:
        raise HTTPException(status_code=400, detail="用户已是项目成员")

    # 添加成员
    await ProjectMember.create(project=project, user=user)

    return {"message": "成员添加成功"}


@router.delete("/{project_id}/members/{user_id}")
async def remove_project_member(
        project_id: int,
        user_id: int,
        current_user: User = Depends(get_current_user)
):
    """移除项目成员"""
    project = await get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 检查成员关系是否存在
    membership = await ProjectMember.get_or_none(project=project, user_id=user_id)
    if not membership:
        raise HTTPException(status_code=404, detail="用户不是项目成员")

    # 移除成员
    await membership.delete()

    return {"message": "成员已移除"}
