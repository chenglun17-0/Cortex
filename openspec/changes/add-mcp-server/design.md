# Design: MCP Server Architecture

## Architecture Overview

```
┌─────────────────┐     MCP Protocol      ┌──────────────────┐
│  AI System      │ <────────────────────> │  Cortex MCP      │
│  (Claude/Cline) │   stdio / HTTP        │  Server          │
└─────────────────┘                        └──────────────────┘
                                                   │
                                                   │ subprocess
                                                   ▼
                                          ┌──────────────────┐
                                          │  Cortex CLI      │
                                          │  (ctx commands)  │
                                          └──────────────────┘
                                                   │
                                                   │ HTTP / JWT
                                                   ▼
                                          ┌──────────────────┐
                                          │  Cortex Backend  │
                                          │  (FastAPI)       │
                                          └──────────────────┘
```

## Component Design

### 1. MCP Server (`cortex_mcp/server.py`)

**职责**：
- 实现 MCP 协议（stdio 通信）
- 定义 Tools（list_tasks, start_task, submit_pr, complete_task, get_task_status）
- 处理 AI 调用并转换为 CLI 命令

**通信方式**：
- 使用 stdio 进行 JSON-RPC 通信
- 返回 JSON 格式的结构化数据

**Tool 定义**：
```python
Tools = [
    list_tasks() -> 列出当前用户任务
    start_task(task_id) -> 开始任务
    submit_pr(commit_message?) -> 提交 PR
    complete_task() -> 完成任务
    get_task_status() -> 获取当前分支状态
]
```

### 2. CLI Enhancement (`cli/commands/tasks.py`)

**职责**：
- 添加 `--json` 参数支持结构化输出
- 保持现有功能不变（向后兼容）

**变更**：
```python
def list_tasks(json_output: bool = False):
    # 如果 json_output=True，返回 JSON 格式
    # 否则保持现有的表格输出
```

### 3. Configuration (`pyproject.toml`)

**依赖添加**：
```toml
dependencies = [
    ...,
    "mcp"  # MCP SDK
]
```

**入口点**：
```toml
[project.scripts]
cortex-mcp = "cortex_mcp.server:main"
```

## Data Flow

### Scenario: AI starts a task

1. **AI System** → MCP Server: `call_tool("start_task", {task_id: 42})`
2. **MCP Server** → CLI: `subprocess.run(["ctx", "tasks", "start", "42"])`
3. **CLI** → Backend: `PATCH /tasks/42 {status: "IN_PROGRESS"}`
4. **CLI** → Git: `git checkout -b feature/task-42-xxx`
5. **CLI** → MCP Server: stdout (执行结果)
6. **MCP Server** → AI: JSON-RPC response with result

### Scenario: AI lists tasks

1. **AI System** → MCP Server: `call_tool("list_tasks", {})`
2. **MCP Server** → CLI: `ctx tasks list --json`
3. **CLI** → Backend: `GET /tasks/`
4. **CLI** → MCP Server: JSON output
5. **MCP Server** → AI: parsed JSON as TextContent

## Integration Points

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["/path/to/cortex-backend/cortex_mcp/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/cortex-backend"
      }
    }
  }
}
```

### Error Handling

- CLI 命令失败 → 返回 JSON with `{"success": false, "error": "..."}`
- 网络超时 → 设置 timeout (30s for list, 60s for git operations)
- 未登录 → CLI 返回错误，MCP 透传给 AI

## Trade-offs

### Approach 1: Subprocess (Chosen) ✅
**优点**：
- 实现简单，复用现有 CLI 逻辑
- CLI 和 MCP 逻辑完全解耦
- 易于测试和维护

**缺点**：
- 每次调用都启动新进程（性能开销）
- 需要处理进程间通信

### Approach 2: Direct API Calls
**优点**：
- 性能更好（直接 HTTP 调用）
- 无进程开销

**缺点**：
- 需要重复实现 CLI 中的业务逻辑（Git 操作等）
- 代码重复，维护成本高

**决策**：选择 **Approach 1 (Subprocess)**，因为：
1. CLI 已有完整的业务逻辑和错误处理
2. MCP 作为集成层，不应重复实现
3. 性能开销对 AI 交互场景可接受

## Security Considerations

1. **认证复用**：MCP Server 通过 CLI 的认证机制（JWT token）
2. **权限隔离**：MCP 继承 CLI 用户的权限
3. **输入验证**：所有参数经过 CLI 的验证逻辑
4. **Secrets 保护**：不直接访问 API，避免暴露凭证

## Future Enhancements

1. **Resources 支持**：暴露任务数据作为 MCP Resources
2. **Prompts 支持**：预定义提示模板（如 "创建新任务"）
3. **Notifications**：任务状态变更时主动通知 AI
4. **SSE/HTTP 传输**：支持非 stdio 的通信方式
