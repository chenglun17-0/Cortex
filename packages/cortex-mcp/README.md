# @cortex/cli-mcp

Cortex CLI MCP Server - Connect Claude Desktop, Cline, Cursor to Cortex task management.

## Installation

```bash
npm install -g @cortex/cli-mcp
```

Or use directly with npx (no installation needed):

```bash
npx @cortex/cli-mcp@latest
```

## Usage

The MCP server automatically exposes the following tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_tasks` | List assigned tasks | None |
| `start_task` | Start a task | `task_id` (number) |
| `submit_pr` | Submit PR | `commit_message` (string, optional) |
| `complete_task` | Complete task | None |
| `get_task_status` | Get current task status | None |

## Configuration

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Cline (VS Code)

Add to VS Code settings:

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

Add to Cursor settings:

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

Edit `~/.continue/config.json`:

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

## Prerequisites

- Node.js >= 18.0.0
- Cortex CLI (`ctx`) installed and configured
- Active Cortex session (run `ctx auth login`)

## Migration from Python MCP

If you were previously using the Python-based MCP server:

1. Update your configuration to use the npm package (see examples above)
2. The Python MCP server has been deprecated
3. All functionality is preserved in this package

## License

MIT

## Support

For issues and feature requests, please visit the Cortex project repository.
