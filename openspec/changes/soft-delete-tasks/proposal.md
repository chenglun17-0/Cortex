# Change: 任务软删除功能

## Why
当前任务删除采用硬删除方式，可能导致数据丢失风险且无法恢复。需要实现软删除机制以保护数据安全，支持误删恢复。

## What Changes
- Task 模型新增 `deleted_at` 字段
- 删除任务接口改为软删除（设置 deleted_at）
- 查询任务时默认过滤已删除任务
- 恢复任务接口（可选，实现软删除后恢复）

## Impact
- Affected specs: tasks
- Affected code:
  - 后端: `app/models/task.py`, `app/schemas/task.py`, `app/api/v1/endpoints/tasks.py`
  - 前端: `types/index.ts`, `features/tasks/service.ts`
