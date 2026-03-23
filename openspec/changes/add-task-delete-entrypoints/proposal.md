# Change: 补齐任务删除入口（CLI 与网页端）

## Why
后端已经支持任务软删除、列表过滤和基础权限校验，但当前仓库缺少面向用户的删除入口：`ctx tasks` 没有删除命令，Web 端任务页面也没有删除操作。结果是删除能力虽然存在，却无法通过标准工作流触达，也没有形成“删除后列表/详情同步刷新”和错误反馈闭环。

## What Changes
- 为 `ctx tasks` 增加删除命令，显式按任务 ID 删除任务
- 在 Web 任务页面提供删除入口与二次确认
- 删除成功后统一刷新任务列表、任务详情和项目看板相关缓存，使删除结果立即同步到界面
- 明确删除操作沿用后端现有任务访问权限；CLI 和 Web 对 `403/404` 等失败结果给出清晰提示
- 补充 CLI、前端和端到端验证

## Impact
- Affected specs:
  - `cli`
  - `frontend-task-ui`
- Affected code:
  - `cortex-backend/cli/commands/tasks.py`
  - `cortex-frontend/src/features/tasks/service.ts`
  - `cortex-frontend/src/features/tasks/TaskDetailPage.tsx`
  - `cortex-frontend/src/features/tasks/TaskListPage.tsx`
  - 相关 CLI / 前端测试与验证脚本
