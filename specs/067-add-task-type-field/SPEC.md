---
title: 添加任务类型字段支持多种分支类型
status: completed
priority: medium
tags: [cli, ctx, branch-naming, task-management, database, frontend]
created: 2026-01-17
completed: 2026-01-17
---

# 概述

添加 `type` 字段到任务模型，支持创建不同类型任务时生成对应分支名。

## 目标

1. 数据库添加 `type` 字段
2. 前端新建任务表单添加类型选择
3. CLI 使用任务类型生成分支名

## 任务类型定义

| 类型 | 说明 | 分支前缀 |
|------|------|----------|
| feature | 新功能 | `feature/` |
| bug | Bug 修复 | `bug/` |
| docs | 文档更新 | `docs/` |
| fix | 简单修复 | `fix/` |
| chore | 构建/工具 | `chore/` |
| refactor | 重构 | `refactor/` |

## 实现方案

### 1. 数据库

**文件**: `app/models/task.py`

```python
class Task(Model):
    type = fields.CharField(max_length=20, default="feature", index=True)  # 新增
```

### 2. Schema

**文件**: `app/schemas/task.py`

```python
class TaskBase(BaseModel):
    type: str = "feature"  # 新增

class TaskCreate(TaskBase):
    type: str = "feature"  # 新增，必填

class TaskUpdate(BaseModel):
    type: Optional[str] = None  # 新增

class TaskRead(TaskBase):
    type: str  # 新增
```

### 3. 前端

**文件**: `features/tasks/KanbanBoard.tsx`

```tsx
// 在 Form 中添加任务类型选择（在 title 之后）

<Form.Item
    name="type"
    label="任务类型"
    initialValue="feature"
    rules={[{ required: true, message: '请选择任务类型' }]}
>
    <Select style={{ borderRadius: 6 }}>
        <Option value="feature">新功能 (feature)</Option>
        <Option value="bug">Bug 修复 (bug)</Option>
        <Option value="docs">文档更新 (docs)</Option>
        <Option value="fix">修复 (fix)</Option>
        <Option value="chore">构建 (chore)</Option>
        <Option value="refactor">重构 (refactor)</Option>
    </Select>
</Form.Item>

// handleCreate 函数添加 type 传递
const handleCreate = (values: any) => {
    if (!projectId) return;
    createTaskMutation.mutate({
        ...values,
        project_id: Number(projectId),
        status: TaskStatus.TODO,
        deadline: values.deadline?.format('YYYY-MM-DD'),
    });
};
```

### 4. CLI

**文件**: `cli/commands/tasks.py`

```python
# start 函数修改
task = response.json()
branch_name = task.get('branch_name')
branch_type = task.get('type', 'feature')  # 新增：从任务获取类型

is_new_branch = False
if not branch_name:
    branch_name = generate_random_branch_name(task_id, branch_type)  # 新增：传递类型
    is_new_branch = True
```

### 5. 数据库迁移

使用 aerich 生成迁移文件。

## 验收标准

- [ ] 数据库添加 `type` 字段
- [ ] Schema 支持 type 参数
- [ ] 前端新建任务表单包含类型选择
- [ ] CLI start 使用任务类型生成分支名
- [ ] 分支命名正确（如 bug/task-1-abc123）

## 文件位置

| 层级 | 文件路径 |
|------|----------|
| 后端 Model | `app/models/task.py` |
| 后端 Schema | `app/schemas/task.py` |
| 前端 | `features/tasks/KanbanBoard.tsx` |
| CLI | `cli/commands/tasks.py` |
