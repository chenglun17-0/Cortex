# Change: Frontend Task Management UI

## Why
当前 CLI 已完成任务状态流转功能（`start`, `pr`, `done`），但 Web 前端缺少对应的任务管理界面，无法实现"CLI 开发端 → Web 管理端"的双端协同闭环。用户无法通过 Web 界面查看、管理和监控任务进度，这违背了项目"Web 管理端 + CLI 开发端"双端协同的核心设计理念。

## What Changes
- 新增前端任务列表页面：展示分配给当前用户的任务，支持按状态、优先级、项目筛选
- 新增前端任务详情页面：查看任务完整信息，支持编辑任务属性（标题、描述、状态、优先级等）
- 新增前端敏捷看板页面：类似 Tower/Linear 的看板视图，支持拖拽任务卡片在不同状态列之间流转
- 新增前端任务 API 调用：集成后端 `/api/v1/tasks/` 接口，使用 React Query 进行数据管理
- 新增前端路由配置：添加 `/tasks`, `/tasks/:id`, `/board` 路由

## Impact
- Affected specs: `frontend-task-ui` (新增能力)
- Affected code:
  - 前端新增 `src/pages/Tasks/` 目录（任务列表、详情、看板页面）
  - 前端新增 `src/components/TaskCard`, `src/components/TaskBoard` 组件
  - 前端新增 `src/services/taskService.ts` API 调用层
  - 前端修改 `src/router/routes.tsx` 添加新路由
  - 前端修改 `src/layouts/MainLayout.tsx` 添加导航菜单项
