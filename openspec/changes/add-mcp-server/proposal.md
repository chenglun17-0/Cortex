# Change: MCP Server Integration

## Why
Cortex 的长期规划包含 **AI 智能辅助能力**（LangChain + RAG 实现工单智能聚合、代码智能辅助），但目前缺少 AI 系统与 Cortex 集成的标准化方式。

当前问题：
1. **CLI 功能完善但 AI 无法直接调用**：`ctx tasks start/pr/done` 已实现完整的任务状态流转，但 AI 系统无法通过标准协议调用
2. **缺少双向交互**：AI 需要能够获取任务列表（作为 context）并调用命令（执行操作）
3. **生态隔离**：无法被 Claude Desktop、Cline、Cursor 等 AI 工具使用，限制了 AI 辅助开发的潜力

## What Changes
- **新增 cortex_mcp 模块**：实现 MCP (Model Context Protocol) 服务器
- **封装 CLI 命令为 MCP Tools**：
  - `list_tasks` - 列出任务（作为 AI 的 context）
  - `start_task` - 开始任务（创建分支、更新状态）
  - `submit_pr` - 提交 PR（推送代码、创建 PR）
  - `complete_task` - 完成任务（清理分支）
  - `get_task_status` - 获取当前任务状态
- **添加 JSON 输出支持**：CLI 支持 `--json` 参数，输出结构化数据便于 AI 解析
- **提供配置文档**：Claude Desktop 配置示例、集成指南

## Impact
- Affected specs: `mcp-integration` (新增能力)
- Affected code:
  - 后端新增 `cortex_mcp/` 目录（MCP 服务器实现）
  - 后端修改 `cli/commands/tasks.py`（添加 JSON 输出）
  - 后端修改 `pyproject.toml`（添加 mcp 依赖）
  - 文档新增 `docs/mcp-integration.md`（配置指南）

## Benefits
1. **标准化集成**：AI 系统可通过开放协议调用 Cortex CLI
2. **生态兼容**：支持 Claude Desktop、Cline、Cursor 等主流 AI 工具
3. **能力保留**：CLI 命令继续供开发者直接使用，MCP 作为额外集成层
4. **AI 增强开发**：为后续 AI 辅助（自动生成 commit message、智能代码审查）打基础
