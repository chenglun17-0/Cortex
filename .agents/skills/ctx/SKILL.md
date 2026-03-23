---
name: ctx
description: 使用 Cortex CLI `ctx` 处理任务流转、认证、配置和 AI 审查。凡是用户提到 `ctx`、任务开始/提单/提 PR/完成任务、CLI 配置、登录 Cortex、AI code review，或希望按项目规范推进 Cortex 工单时，都应优先使用这个 skill，而不是手写零散 git/API 步骤。
---

# ctx

用于在 Cortex 项目中安全、准确地使用 `ctx` CLI。

## 何时使用

出现以下任一场景时触发：

- 用户要求使用 `ctx` 创建、查看、开始、提交或完成任务
- 用户要求登录/登出 Cortex CLI
- 用户要求查看或修改 `ctx` 配置
- 用户要求运行或配置 AI 代码审查
- 用户已经在 Cortex 任务分支上，希望你按项目约定继续推进任务流

如果用户只是要普通 Git 操作、普通代码修改、或与 Cortex CLI 无关的终端任务，不要触发本 skill。

## 核心原则

1. 先判断意图属于 `auth`、`tasks`、`config` 还是 `review`。
2. 命令不确定时，先运行 `ctx --help` 或对应子命令的 `--help`，不要凭记忆猜参数。
3. 涉及网络访问、登录、任务状态变更、创建分支/worktree、push、创建 PR、发布 review、完成任务、写入配置前，先向工程师说明影响和回滚方式，再执行。
4. `ctx` 只是项目工作流入口，不替代代码验证；命令执行后仍要核对结果。
5. 不读取 `.env*`、`config/credentials*`、`secrets/**` 来“帮忙找配置”。

## 执行流程

### 1. 识别目标

先把请求归入一种主路径：

- `auth`：登录或登出 Cortex
- `tasks`：新建、查看、开始、提 PR、完成任务
- `config`：查看配置、查看可用键、设置配置
- `review`：运行 AI 审查或切换审查开关

如果请求模糊，先澄清目标动作和验收结果，再执行命令。

### 2. 做最小必要检查

根据动作补最少的前置检查：

- `tasks start/pr/done/review run`：确认当前目录是 Git 仓库
- `tasks pr/done/review run`：确认当前分支是否符合 `feature|bug|docs|fix|chore|refactor/task-<id>-<suffix>`
- `tasks new`：优先确认 `default_project_id` 已配置
- `review run --publish`：确认已配置 Git provider token，且用户同意发布到 PR

### 3. 执行并回报

执行命令后，回报这些内容：

- 执行的命令
- 关键结果，例如任务 ID、状态变化、分支名、PR URL、配置变化
- 是否存在人工交互或后续步骤
- 若失败，给出最短可执行的下一步

## 命令路由

### auth

- `ctx auth login`
  - 交互式输入邮箱和密码
  - 会向后端发送登录请求并把 token 写入 `~/.cortex/config.json`
  - 这是网络和凭证写入操作，必须先确认
- `ctx auth logout`
  - 清空本地 `access_token`

### tasks

- `ctx tasks new "<title>" <YYYY-MM-DD> --type <type> --priority <priority> --desc "<desc>"`
  - 通过后端 API 创建任务
  - 依赖 `default_project_id`
  - `type` 默认 `feature`，`priority` 默认 `medium`

- `ctx tasks list`
- `ctx tasks list --json`
  - 查看当前用户任务列表

- `ctx tasks start <task_id> [--worktree|--no-worktree]`
  - 将任务置为 `IN_PROGRESS`
  - 若任务未绑定分支，会生成 `{type}/task-{id}-{8位随机后缀}`
  - 可能创建 worktree 并切换目录/分支

- `ctx tasks pr [--ai|--no-ai]`
  - 从当前任务分支识别任务 ID
  - 如有未提交改动，会先暂存、再生成或要求输入 commit message
  - 更新状态为 `REVIEW`
  - push 分支并尝试创建 PR/MR
  - 默认启用 AI 生成 commit message 和 PR 描述
  - 这是提交、推送、建 PR 的高风险操作，必须先确认

- `ctx tasks done`
  - 适用于远程已合并后的收尾
  - 会切回主分支并 `pull`
  - 更新任务状态为 `DONE`
  - 是否删除 worktree / 本地分支 / 远程分支取决于配置
  - 这是状态流转和 Git 清理操作，必须先确认

### config

- `ctx config list`
- `ctx config keys`
- `ctx config set <key> <value>`

常见配置键：

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

额外说明：

- `ctx review status` 实际还会读写 `ai_review_enabled`
- 布尔值支持 `true/false`
- `default_project_id` 会被解析为整数
- `git_provider` 仅支持 `github` 或 `gitlab`
- `ai_provider` 支持 `openai`、`anthropic`、`local`

### review

- `ctx review run`
  - 基于当前任务分支与主分支 diff 执行 AI 审查
  - 需要当前分支名符合任务分支模式
  - 没有 diff 时会直接退出

- `ctx review run --publish`
  - 审查并发布到 PR 评论区
  - 需要 Git provider 和对应 token
  - 涉及远程写操作，必须先确认

- `ctx review status --show`
- `ctx review status --enable`
- `ctx review status --disable`

## 风险提示

以下操作默认视为需要确认：

- `ctx auth login`
- `ctx tasks new`
- `ctx tasks start`
- `ctx tasks pr`
- `ctx tasks done`
- `ctx config set`
- `ctx review run --publish`
- 任何会触发网络访问、状态流转、Git push、PR 发布、配置写入的 `ctx` 命令

建议回滚思路：

- 配置写错：使用 `ctx config set` 改回原值
- 分支切换或 worktree 创建不符合预期：停止后人工检查当前目录与分支
- `tasks pr` 后状态或提交不符合预期：先不要继续 `done`，改完代码后重新提交
- `tasks done` 前如果远程未合并，不要执行

## 输出要求

执行 `ctx` 相关任务时，尽量按下面结构汇报：

```md
目标：<用户想完成的事>
检查：<做了哪些前置检查>
执行：<运行的 ctx 命令>
结果：<状态变化 / 分支 / PR / 配置结果>
后续：<还需要用户确认或继续执行的步骤>
```

## 参考资料

需要参数或示例时，继续查看 [references/commands.md](./references/commands.md)。
