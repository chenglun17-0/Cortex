# ctx 命令速查

本文档汇总当前仓库内 `ctx` CLI 的常用命令、参数和真实行为，供 `ctx` skill 按需读取。

## 顶层命令

```bash
ctx --help
```

可用命令：

- `auth`
- `tasks`
- `config`
- `review`

## auth

```bash
ctx auth --help
ctx auth login
ctx auth logout
```

说明：

- `login` 会交互式提示 `Email` 和 `Password`
- 登录成功后会把 `access_token` 写入 `~/.cortex/config.json`
- `logout` 会把 `access_token` 清空

## tasks

```bash
ctx tasks --help
```

### 新建任务

```bash
ctx tasks new "任务标题" 2026-03-31 --type feature --priority medium --desc "任务描述"
```

参数：

- `title`：必填
- `deadline`：必填，格式 `YYYY-MM-DD`
- `--type/-t`：默认 `feature`
- `--priority/-p`：默认 `medium`
- `--desc/-d`：可选描述

实现约束：

- 依赖配置 `default_project_id`
- 创建请求会把优先级转成大写
- 描述会被写成 `[type]\n描述` 或 `[type]`

### 查看任务

```bash
ctx tasks list
ctx tasks list --json
```

### 开始任务

```bash
ctx tasks start 9
ctx tasks start 9 --no-worktree
```

参数：

- `task_id`：必填
- `--worktree/--no-worktree`：可选；未显式传参时读取配置 `use_worktree`

实现约束：

- 会把任务状态更新为 `IN_PROGRESS`
- 若任务无分支名，会生成 `{type}/task-{id}-{8位随机后缀}`
- 可能创建 worktree 并切换到新目录

### 提交任务 / 创建 PR

```bash
ctx tasks pr
ctx tasks pr --no-ai
```

参数：

- `--ai/--no-ai`：默认启用 AI

实现约束：

- 当前分支必须匹配 `{type}/task-{id}-{suffix}`
- 若工作区有未提交变更，会自动暂存全部改动
- AI 开启时，会尝试生成 commit message 和 PR 描述
- 更新任务状态为 `REVIEW`
- push 到远程后尝试创建 PR/MR

### 完成任务

```bash
ctx tasks done
```

实现约束：

- 仅适用于远程已合并
- 会切回主分支并执行 `pull`
- 更新任务状态为 `DONE`
- 会按配置决定是否删除 worktree、本地分支、远程分支

相关配置：

- `delete_worktree_on_done`
- `delete_local_on_done`
- `delete_remote_on_done`

## config

```bash
ctx config --help
ctx config list
ctx config keys
ctx config set use_worktree true
```

当前代码中显式支持的配置键：

- `url`
- `git_main_branch`
- `default_project_id`
- `access_token`
- `delete_local_on_done`
- `delete_remote_on_done`
- `delete_worktree_on_done`
- `use_worktree`
- `git_provider`
- `github_token`
- `gitlab_token`
- `ai_provider`
- `ai_api_key`
- `ai_model`
- `ai_base_url`

校验规则：

- 布尔键只接受 `true/false`
- `default_project_id` 必须是整数
- `git_provider` 仅支持 `github`、`gitlab`
- `ai_provider` 仅支持 `openai`、`anthropic`、`local`
- `url` 与 `ai_base_url` 必须是 `http://` 或 `https://`

## review

```bash
ctx review --help
```

### 执行 AI 审查

```bash
ctx review run
ctx review run --publish
```

说明：

- 当前分支必须匹配任务分支模式
- 依赖当前分支相对主分支存在 diff
- `--publish/-p` 会把结果发到 PR 评论区

### 查看或切换审查开关

```bash
ctx review status --show
ctx review status --enable
ctx review status --disable
```

实现约束：

- `review status` 实际读写 `ai_review_enabled`
- `--show` 还会显示 `ai_review_dimensions`，为空时视为“默认全部”

## 使用建议

如果对参数、行为或输出仍不确定，优先再次运行对应的 `--help`，不要直接假设。`ctx` 与后端 API、Git provider、AI provider 都有耦合，执行失败时优先检查：

1. 当前是否已登录
2. 当前目录是否为 Git 仓库
3. 当前分支名是否符合 Cortex 任务分支规则
4. 相关配置和 token 是否已设置
5. 远程仓库和后端服务是否可访问
