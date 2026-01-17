# Cortex MCP Server Integration Guide

本文档介绍如何将 Cortex MCP 服务器集成到 AI 系统（如 Claude Desktop、Cline、Cursor 等）。

## 快速开始（Claude Desktop）

### 1. 找到配置文件
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. 添加配置（npm 包方式）

```json
{
  "mcpServers": {
    "cortex": {
      "command": "npx",
      "args": [
        "@cortex/cli-mcp@latest"
      ]
    }
  }
}
```

### 3. 替换路径
无需路径配置，npm 包会自动处理。

### 4. 重启 Claude Desktop
重启应用以加载新的 MCP 服务器。

### 配置说明

| 配置方式 | 适用场景 | 优点 |
|---------|---------|------|
| npm 包 | 所有情况 | 简洁，无需 Python 环境 | 自动依赖管理 |

## 其他 AI 工具配置

### Cline (VS Code)

在 VS Code 设置中添加：

```json
{
  "cline.mcpServers": {
    "cortex": {
      "command": "npx",
      "args": [
        "@cortex/cli-mcp@latest"
      ]
    }
  }
}
```

### Cursor

在 Cursor 设置中添加：

```json
{
  "mcp.servers": {
    "cortex": {
      "command": "npx",
      "args": [
        "@cortex/cli-mcp@latest"
      ]
    }
  }
}
```

### Continue.dev

编辑 `~/.continue/config.json`：

```json
{
  "mcpServers": {
    "cortex": {
      "command": "npx",
      "args": [
        "@cortex/cli-mcp@latest"
      ]
    }
  }
}
```

## 什么是 MCP？

MCP (Model Context Protocol) 是一个开放标准，让 AI 模型能够连接到外部数据源和工具。Cortex MCP 服务器将 Cortex CLI 命令封装为 MCP Tools，使 AI 系统能够执行任务管理操作。

## 可用工具

Cortex MCP 服务器提供以下工具：

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `list_tasks` | 列出分配给当前用户的任务 | 无 |
| `start_task` | 开始任务（创建分支、更新状态） | `task_id` (number) |
| `submit_pr` | 提交代码并创建 PR | `commit_message` (string, 可选) |
| `complete_task` | 完成任务（清理分支） | 无 |
| `get_task_status` | 获取当前任务状态 | 无 |

## 先决条件

- Node.js >= 18.0.0
- Cortex CLI (`ctx`) 已安装并配置
- 活动的 Cortex 会话（运行 `ctx auth login`）

## 从 Python MCP 迁移

如果您之前使用基于 Python 的 MCP 服务器：

1. 更新您的配置以使用 npm 包（参见上文示例）
2. Python MCP 服务器已被弃用
3. 此包保留了所有功能

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

1. **检查 Node.js 版本**：
   ```bash
   node --version
   ```

2. **测试 MCP 服务器**：
   ```bash
   npx @cortex/cli-mcp@latest --help
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

### 使用特定版本

如需使用特定版本：

```json
{
  "mcpServers": {
    "cortex": {
      "command": "npx",
      "args": [
        "@cortex/cli-mcp@1.0.0"
      ]
    }
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
2. 检查 [OpenSpec Issues](../../openspec/changes/refactor-mcp-to-npm/)
3. 在项目中创建 Issue
