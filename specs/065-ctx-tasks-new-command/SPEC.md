---
title: 实现 ctx tasks new 命令（含后端截止时间字段）
status: completed
priority: medium
tags: [cli, ctx, task-management, backend, database, frontend]
created: 2026-01-17
completed: 2026-01-17
---

# 概述

实现 `ctx tasks new` 命令，并为 cortex-backend 添加截止时间（deadline）字段支持。

## 目标

1. 后端 API 支持截止时间字段
2. 数据库添加 deadline 字段
3. 前端新建任务表单添加截止时间选择
4. ctx CLI 新增 `tasks new` 命令

## 需求

### API 参数

| 参数 | 必填 | 默认值 | 类型 | 说明 |
|------|------|--------|------|------|
| title | 是 | - | str | 任务标题 |
| project_id | 是 | - | int | 项目 ID |
| deadline | 是 | - | date | 截止日期 |
| description | 否 | None | str | 任务描述 |
| priority | 否 | MEDIUM | str | 优先级 (LOW, MEDIUM, HIGH) |
| status | 否 | TODO | str | 状态 |
| assignee_id | 否 | None | int | 负责人 ID |

### CLI 参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| title | 是 | - | 任务标题 |
| deadline | 是 | - | 截止日期 (YYYY-MM-DD) |
| type | 否 | feature | 任务类型 |
| priority | 否 | medium | 优先级 |
| description | 否 | 空 | 任务描述 |

## 实现方案

### 1. 数据库
- 文件: `app/models/task.py`
- 添加: `deadline = fields.DateField(null=True)`

### 2. 后端 Schema
- 文件: `app/schemas/task.py`
- TaskCreate: 添加 `deadline: date`（必填）
- TaskRead: 添加 `deadline: Optional[date]`

### 3. 前端
- 文件: `KanbanBoard.tsx`
- 在 Form 中添加 DatePicker 组件（截止日期，必填）
- 更新 handleCreate 处理日期格式

### 4. CLI 命令
- 文件: `cli/commands/tasks.py`
- 新增 `@app.command(name="new")` 函数
- 验证日期格式，构建请求数据，调用 API

### 5. 命令使用

```bash
# 最小参数
ctx tasks new "任务标题" 2026-02-01

# 完整参数
ctx tasks new "任务标题" 2026-02-01 --type feature --priority high --desc "描述"
```

## 验收标准

- [ ] 数据库添加 `deadline` 字段
- [ ] 后端 API 支持 deadline 参数
- [ ] 前端新建任务表单包含截止日期选择
- [ ] `ctx tasks new` 命令可用
- [ ] 支持必填参数：title, deadline
- [ ] 支持可选参数：type, priority, description

## 文件位置

| 层级 | 文件路径 |
|------|----------|
| CLI | `cli/commands/tasks.py` |
| 后端 API | `app/api/v1/endpoints/tasks.py` |
| 后端 Schema | `app/schemas/task.py` |
| 后端 Model | `app/models/task.py` |
| 前端 | `features/tasks/KanbanBoard.tsx` |
