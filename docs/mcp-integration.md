# Cortex MCP Server Integration Guide

本文档介绍如何将 Cortex MCP 服务器集成到 AI 系统（如 Claude Desktop、Cline、Cursor 等）。

## 快速开始（Claude Desktop）

### 1. 找到配置文件
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. 添加配置（方式1：简洁推荐）

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
        "PYTHONPATH": "/Users/jal/school/Cortex/cortex-backend"
      }
    }
  }
}
```

### 3. 添加配置（方式2：处理架构问题）

如果遇到架构不兼容问题，使用启动脚本：

```json
{
  "mcpServers": {
    "cortex": {
      "command": "/Users/jal/school/Cortex/cortex-backend/start-mcp.sh",
      "args": []
    }
  }
}
```

### 4. 替换路径
将 `/Users/jal/school/Cortex/cortex-backend` 替换为你的实际路径

### 5. 重启 Claude Desktop
重启应用以加载新的 MCP 服务器

### 配置说明

| 配置方式 | 适用场景 | 优点 | 缺点 |
|---------|---------|------|------|
| Python 模块 | 大多数情况 | 简洁，类似 npm 包 | 可能遇到架构问题 |
| 启动脚本 | 架构不兼容时 | 自动检测和修复 | 需要绝对路径 |

## 其他 AI 工具配置

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

### 配置对比

| AI 工具 | 配置文件位置 | 配置键 |
|---------|------------|--------|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` | `mcpServers` |
| Cline (VS Code) | VS Code Settings | `cline.mcpServers` |
| Cursor | Cursor Settings | `mcp.servers` |
| Continue.dev | `~/.continue/config.json` | `mcpServers` |
| 自定义 Agent | 代码中配置 | 使用 MCP SDK |

## 使用绝对路径的替代方案

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

## Cline (VS Code Extension) 配置

Cline 是 VS Code 的 AI 助手扩展，支持 MCP。

### 1. 安装 Cline
在 VS Code 中搜索并安装 "Cline" 扩展

### 2. 配置 MCP（简洁方式）

```json
{
  "cline.mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "cortex_mcp.server"],
      "env": {
        "PYTHONPATH": "/Users/jal/school/Cortex/cortex-backend"
      }
    }
  }
}
```

### 3. 配置 MCP（脚本方式）

```json
{
  "cline.mcpServers": {
    "cortex": {
      "command": "/Users/jal/school/Cortex/cortex-backend/start-mcp.sh"
    }
  }
}
```

### 4. 重启 VS Code
使配置生效

## Cursor 配置

Cursor 是基于 AI 的代码编辑器，内置 MCP 支持。

### 1. 打开设置
`Cmd+,` → 搜索 "MCP"

### 2. 添加 MCP 服务器（简洁方式）

```json
{
  "mcp.servers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "cortex_mcp.server"],
      "env": {
        "PYTHONPATH": "/Users/jal/school/Cortex/cortex-backend"
      }
    }
  }
}
```

### 3. 添加 MCP 服务器（脚本方式）

```json
{
  "mcp.servers": {
    "cortex": {
      "command": "/Users/jal/school/Cortex/cortex-backend/start-mcp.sh"
    }
  }
}
```

### 4. 重启 Cursor

## Continue.dev 配置

Continue 是 VS Code/JetBrains 的 AI 助手。

### 1. 安装 Continue
在 VS Code 中安装 "Continue" 扩展

### 2. 编辑配置文件
位置：`~/.continue/config.json`

**简洁方式**：
```json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "cortex_mcp.server"],
      "env": {
        "PYTHONPATH": "/Users/jal/school/Cortex/cortex-backend"
      }
    }
  }
}
```

**脚本方式**：
```json
{
  "mcpServers": {
    "cortex": {
      "command": "/Users/jal/school/Cortex/cortex-backend/start-mcp.sh"
    }
  }
}
```

## 自定义 Agent 配置

如果你正在开发自定义 AI Agent，可以使用 MCP SDK 直接集成。

### Python 示例

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 创建 MCP 客户端
server_params = StdioServerParameters(
    command="python",
    args=["-m", "cortex_mcp.server"],
    env={
        "PYTHONPATH": "/path/to/cortex-backend"
    }
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()

            # 列出工具
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

            # 调用工具
            result = await session.call_tool("list_tasks", {})
            print(result.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### JavaScript/Node.js 示例

```javascript
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

const transport = new StdioClientTransport({
  command: 'python',
  args: ['-m', 'cortex_mcp.server'],
  env: {
    PYTHONPATH: '/path/to/cortex-backend'
  }
});

const client = new Client({
  name: 'my-agent',
  version: '1.0.0'
});

async function main() {
  await client.connect(transport);

  // 初始化
  await client.initialize();

  // 列出工具
  const tools = await client.listTools();
  console.log('Available tools:', tools.tools.map(t => t.name));

  // 调用工具
  const result = await client.callTool({
    name: 'list_tasks',
    arguments: {}
  });
  console.log(result.content);
}

main().catch(console.error);
```

## 验证配置

### 方法 1: 在 Claude Desktop 中验证

1. 打开 Claude Desktop
2. 在对话中输入："列出我的任务"
3. 如果配置正确，AI 会调用 `list_tasks` 工具

### 方法 2: 查看日志

**Claude Desktop 日志位置**：
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`
- Linux: `~/.config/Claude/logs/`

查找 `mcp-server-cortex.log` 文件，检查是否有错误。

### 方法 3: 测试 MCP 服务器

```bash
cd cortex-backend
./start-mcp.sh --help
```

或直接测试：
```bash
cd cortex-backend
source .venv/bin/activate
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python -m cortex_mcp.server
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
