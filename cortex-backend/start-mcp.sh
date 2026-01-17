#!/bin/bash
# Cortex MCP 启动脚本 - 强制使用 arm64 架构

cd "$(dirname "$0")"
source .venv/bin/activate
arch -arm64 python -m cortex_mcp.server "$@"
