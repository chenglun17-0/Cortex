# Change: Refactor MCP Server to NPM Package

## Why
当前 MCP 服务器使用 Python 实现，存在以下问题：
1. **部署复杂**：需要配置 PYTHONPATH、虚拟环境，对非 Python 开发者不友好
2. **生态不统一**：MCP SDK 生态以 TypeScript/JavaScript 为主，Python 版本维护成本高
3. **配置繁琐**：需要处理 Python 架构兼容性问题（如 start-mcp.sh 脚本）
4. **用户体验差**：无法像 `npx @browsermcp/mcp@latest` 那样一行命令启动

## What Changes
- **新增 cortex-mcp npm 包**：使用 TypeScript 重写 MCP 服务器
- **保留所有现有功能**：list_tasks, start_task, submit_pr, complete_task, get_task_status
- **简化部署方式**：支持 `npx @cortex/cli-mcp@latest` 一行命令启动
- **移除 Python MCP**：废弃 cortex_backend/cortex_mcp 模块
- **更新文档**：提供 npm 包配置示例

## Impact
- Affected specs: `mcp-integration` (MODIFIED)
- Affected code:
  - 新增 `packages/cortex-mcp/` 目录（TypeScript MCP 服务器）
  - 删除 `cortex-backend/cortex_mcp/` 目录
  - 修改 `cortex-backend/pyproject.toml`（移除 cortex-mcp 入口）
  - 更新 `docs/mcp-integration.md`（npm 包配置指南）

## Benefits
1. **部署简化**：用户无需 Python 环境，一条 npx 命令即可
2. **生态统一**：使用主流的 @modelcontextprotocol/sdk-typescript，社区支持更好
3. **配置清晰**：类似其他 MCP 包的配置方式（如 @browsermcp/mcp）
4. **维护成本低**：TypeScript 生态工具链完善，开发体验更好
