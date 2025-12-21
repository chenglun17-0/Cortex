from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.project import ProjectCreate, ProjectRead
from app.models import Project, ProjectMember, User
from app.api.deps import get_current_user

router = APIRouter()


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

    return project


@router.get("/", response_model=List[ProjectRead])
async def read_my_projects(
        current_user: User = Depends(get_current_user)
):
    # 查询我参与的所有项目
    projects = await Project.filter(members__id=current_user.id).all()
    return projects