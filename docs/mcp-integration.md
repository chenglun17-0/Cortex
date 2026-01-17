# Cortex MCP Server Integration Guide

本文档介绍如何将 Cortex MCP 服务器集成到 AI 系统（如 Claude Desktop、Cline、Cursor 等）。

## 什么是 MCP？

MCP (Model Context Protocol) 是一个开放标准，让 AI 模型能够连接到外部数据源和工具。Cortex MCP 服务器将 Cortex CLI 命令封装为 MCP Tools，使 AI 系统能够执行任务管理操作。

## 可用工具

Cortex MCP 服务器提供以下工具：

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `list_tasks` | 列出分配给当前用户的任务 | 无 |
| `start_task` | 开始任务（创建分支、更新状态） | `task_id` (integer) |
| `submit_pr` | 提交代码并创建 PR | `commit_message` (string, 可选) |
| `complete_task` | 完成任务（清理分支） | 无 |
| `get_task_status` | 获取当前任务状态 | 无 |

## 安装

### 1. 安装依赖

```bash
cd cortex-backend
pip install -e .
```

这将安装 `mcp` 包并注册 `cortex-mcp` 命令。

### 2. 验证安装

```bash
cortex-mcp --help
```

## Claude Desktop 配置

### macOS 配置文件位置

`~/Library/Application Support/Claude/claude_desktop_config.json`

### 配置示例

```json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": [
        "-m",
        "cortex_mcp.server"
      ],
      "env": {
        "PYTHONPATH": "/path/to/cortex-backend"
      }
    }
  }
}
```

**注意事项**：
- 将 `/path/to/cortex-backend` 替换为你的 cortex-backend 目录的绝对路径
- 确保已经通过 `ctx auth login` 登录 Cortex 系统

### 使用绝对路径的替代方案

```json
{
  "mcpServers": {
    "cortex": {
      "command": "/path/to/.venv/bin/python",
      "args": [
        "/path/to/cortex-backend/cortex_mcp/server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/cortex-backend"
      }
    }
  }
}
```

## 使用示例

### 场景 1: AI 查看任务列表

**用户输入**：
```
请列出我当前的任务
```

**AI 调用**：
```javascript
call_tool("list_tasks", {})
```

**返回结果**：
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "实现用户登录功能",
      "status": "TODO",
      "priority": "HIGH",
      "branch_name": null
    },
    {
      "id": 2,
      "title": "修复页面样式问题",
      "status": "IN_PROGRESS",
      "priority": "MEDIUM",
      "branch_name": "feature/task-2-a1b2c3d4"
    }
  ]
}
```

### 场景 2: AI 开始一个任务

**用户输入**：
```
开始任务 #1
```

**AI 调用**：
```javascript
call_tool("start_task", {task_id: 1})
```

**返回结果**：
```json
{
  "success": true,
  "task_id": 1,
  "output": "Task updated to IN_PROGRESS\nSwitched to branch: feature/task-1-x9y8z7w6"
}
```

### 场景 3: AI 提交代码

**用户输入**：
```
我完成了这个任务，帮我提交代码
```

**AI 调用**：
```javascript
call_tool("submit_pr", {
  commit_message: "feat: 实现用户登录功能"
})
```

**返回结果**：
```json
{
  "success": true,
  "commit_message": "feat: 实现用户登录功能",
  "output": "Task status updated to REVIEW\nCode pushed to origin"
}
```

### 场景 4: AI 完成任务

**用户输入**：
```
任务已经合并了，帮我完成它
```

**AI 调用**：
```javascript
call_tool("complete_task", {})
```

**返回结果**：
```json
{
  "success": true,
  "output": "Task status updated to DONE\nSwitched to main branch"
}
```

## 错误处理

### 认证错误

**症状**：
```json
{
  "success": false,
  "error": "Not logged in. Please run 'ctx auth login' first."
}
```

**解决方案**：
在终端中运行 `ctx auth login` 登录 Cortex 系统。

### Git 仓库错误

**症状**：
```json
{
  "success": false,
  "error": "Not in a git repository"
}
```

**解决方案**：
确保在 Git 仓库目录中运行 AI 工具。

### 任务不存在

**症状**：
```json
{
  "success": false,
  "error": "Task #999 not found."
}
```

**解决方案**：
使用 `list_tasks` 查看可用的任务 ID。

## 故障排查

### MCP 服务器无法启动

1. **检查 Python 路径**：
   ```bash
   which python
   # 或
   echo $VIRTUAL_ENV
   ```

2. **测试 MCP 服务器**：
   ```bash
   python -m cortex_mcp.server
   ```

3. **查看 Claude Desktop 日志**：
   - macOS: `~/Library/Logs/Claude/`

### 工具调用失败

1. **验证 CLI 安装**：
   ```bash
   ctx --version
   ```

2. **测试 CLI 命令**：
   ```bash
   ctx tasks list --json
   ```

3. **检查认证状态**：
   ```bash
   ctx config list
   ```

## 高级配置

### 使用虚拟环境

如果你的 Cortex CLI 安装在虚拟环境中，确保配置指向正确的 Python 解释器：

```json
{
  "mcpServers": {
    "cortex": {
      "command": "/path/to/.venv/bin/python",
      "args": [
        "-m",
        "cortex_mcp.server"
      ],
      "env": {
        "PYTHONPATH": "/path/to/cortex-backend",
        "PATH": "/path/to/.venv/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### 环境变量

可以在 `env` 中添加额外的环境变量：

```json
{
  "env": {
    "PYTHONPATH": "/path/to/cortex-backend",
    "CORTEX_API_URL": "http://localhost:8000",
    "CORPLEX_LOG_LEVEL": "DEBUG"
  }
}
```

## 安全建议

1. **不要在配置文件中存储敏感信息**（如密码、token）
2. **使用绝对路径**避免路径混淆
3. **限制 MCP 服务器的权限**，只授予必要的访问权限
4. **定期更新** MCP SDK 和 Cortex CLI

## 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io)
- [Cortex 项目文档](../README.md)
- [OpenSpec 规范](../openspec/AGENTS.md)

## 支持

如果遇到问题，请：
1. 查看 [故障排查](#故障排查) 部分
2. 检查 [OpenSpec Issues](../../openspec/changes/add-mcp-server/)
3. 在项目中创建 Issue
