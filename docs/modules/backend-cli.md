# CLI 模块（`cortex-backend/cli`）

## 1. 模块结构

| 子模块 | 目录/文件 | 职责 |
|--------|-----------|------|
| 命令编排层 | `commands/` | 组织 `ctx auth/tasks/config/review` 命令流程 |
| API 客户端层 | `api.py` | 调用后端接口（Bearer Token） |
| Git 操作层 | `git.py` | 分支/worktree/push/pull/diff 等本地 Git 能力 |
| Provider 适配层 | `providers/` | GitHub/GitLab/Gitee 的 PR/MR 与评论能力 |
| AI 能力层 | `ai/` | commit message、PR 描述、代码审查 |
| 配置中心 | `config.py` | 本地配置读写（`~/.cortex/config.json`） |

## 2. 入口与命令

| 文件 | 说明 |
|------|------|
| `cli/main.py` | Typer 入口，注册 `auth/tasks/config/review` |
| `pyproject.toml` `[project.scripts]` | 声明 `ctx = "cli.main:app"` 可执行入口 |
| `commands/auth.py` | 登录/登出 |
| `commands/tasks.py` | `new/list/start/pr/done` 主工作流 |
| `commands/config.py` | 配置查看与设置 |
| `commands/review.py` | AI 代码审查命令 |

## 3. 典型工作流

```text
ctx tasks start <id>
  -> API 查询/更新任务状态
  -> 生成或切换本地分支/worktree

ctx tasks pr
  -> Git diff + commit
  -> 可选 AI 生成 commit message / PR 描述
  -> Push 并调用 Provider 创建 PR/MR
  -> 状态流转至 REVIEW

ctx tasks done
  -> 切回主分支并更新
  -> 状态流转至 DONE
  -> 按配置清理分支/worktree
```

## 4. 外部交互

| 交互对象 | 方式 | 说明 |
|----------|------|------|
| 后端 API | HTTP | 任务状态与认证 |
| Git 仓库 | 本地命令 | 分支、提交、推送 |
| GitHub/GitLab/Gitee | Provider SDK/API | PR/MR 与评论回写 |
| AI Provider | SDK/API | 文档生成与代码审查 |

## 5. 配置关键项

| 配置项 | 用途 |
|--------|------|
| `url` | 后端 API 地址 |
| `access_token` | 登录凭证 |
| `git_provider` | Git 平台类型 |
| `ai_provider/ai_model/ai_api_key` | AI 能力配置 |
| `use_worktree` | 是否启用 worktree 工作流 |
