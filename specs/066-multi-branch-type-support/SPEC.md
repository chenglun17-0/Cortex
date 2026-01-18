---
title: 支持多种任务类型分支命名规范
status: completed
priority: medium
tags: [cli, ctx, branch-naming, task-management]
created: 2026-01-17
completed: 2026-01-17
---

# 概述

当前分支命名规范只支持 `feature` 类型，需要扩展支持 `bug`、`docs`、`fix` 等多种任务类型。

## 目标

1. 支持多种任务类型分支命名
2. 统一所有代码中的分支匹配模式

## 分支命名规范

### 格式

```
{type}/task-{id}-{random_suffix}
```

### 支持的类型

| 类型 | 说明 | 示例 |
|------|------|------|
| feature | 新功能 | `feature/task-1-a1b2c3d4` |
| bug | Bug 修复 | `bug/task-2-c3d4e5f6` |
| docs | 文档更新 | `docs/task-3-d4e5f6g7` |
| fix | 简单修复 | `fix/task-4-e5f6g7h8` |
| chore | 构建/工具 | `chore/task-5-f6g7h8i9` |
| refactor | 重构 | `refactor/task-6-g7h8i9j0` |

### 正则表达式

```python
r"(feature|bug|docs|fix|chore|refactor)/task-(\d+)-"
```

## 需要修改的位置

| 文件 | 位置 | 当前代码 | 修改后 |
|------|------|----------|--------|
| cli/commands/tasks.py | pr() L203 | `r"feature/task-(\d+)-"` | `r"(feature\|bug\|docs\|fix\|chore\|refactor)/task-(\d+)-"` |
| cli/commands/tasks.py | done() L274 | `r"feature/task-(\d+)-"` | `r"(feature\|bug\|docs\|fix\|chore\|refactor)/task-(\d+)-"` |
| cli/commands/tasks.py | generate_random_branch_name() L322 | `f"feature/task-{task_id}-{random_suffix}"` | 添加 type 参数 |

## 实现方案

### 1. 定义类型常量

```python
BRANCH_TYPES = ["feature", "bug", "docs", "fix", "chore", "refactor"]
BRANCH_PATTERN = re.compile(r"(feature|bug|docs|fix|chore|refactor)/task-(\d+)-")
```

### 2. 修改正则匹配

```python
# pr() 函数
match = BRANCH_PATTERN.match(branch_name)
if not match:
    console.print(f"[red]Current branch '{branch_name}' is not a valid Cortex task branch.[/red]")
    console.print("Branch name must match '{type}/task-{id}-{suffix}'.")
    raise typer.Exit(1)

task_id = int(match.group(2))
branch_type = match.group(1)  # 可选：获取分支类型
```

### 3. 修改分支生成函数

```python
def generate_random_branch_name(task_id: int, branch_type: str = "feature") -> str:
    """
    生成随机分支名
    格式: {type}/task-{id}-{随机8位字符}
    """
    random_suffix = secrets.token_hex(4)
    return f"{branch_type}/task-{task_id}-{random_suffix}"
```

### 4. 更新提示信息

修改所有提示信息中的 "feature/task-{id}-" 为 "{type}/task-{id}-{suffix}"

## 验收标准

- [ ] 正则表达式支持多种分支类型
- [ ] pr() 函数正确提取任务 ID
- [ ] done() 函数正确提取任务 ID
- [ ] generate_random_branch_name() 支持指定类型
- [ ] 错误提示信息准确

## 文件位置

- `cortex-backend/cli/commands/tasks.py`
