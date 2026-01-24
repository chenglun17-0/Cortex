# Change: 增强项目管理系统功能

## Why
当前项目模块仅支持创建和查询功能，缺少更新、删除和成员管理能力。需要完善项目 CRUD 功能以满足完整的项目管理需求。

## What Changes
- 新增项目更新接口（PATCH /projects/{id}）
- 新增项目删除接口（DELETE /projects/{id}），使用软删除，删除前检查关联任务
- 新增项目成员管理接口：
  - 获取成员列表（GET /projects/{id}/members）
  - 添加成员（POST /projects/{id}/members）
  - 移除成员（DELETE /projects/{id}/members/{userId}）
- 新增用户搜索接口（GET /users/search）
- 前端增加项目编辑弹窗
- 前端增加项目成员管理面板
- 更新 ProjectRead schema 增加 members 字段

## Impact
- Affected specs: projects, users
- Affected code:
  - 后端: `app/api/v1/endpoints/projects.py`, `app/schemas/project.py`
  - 前端: `features/projects/ProjectsPage.tsx`, `types/index.ts`
