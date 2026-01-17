#!/bin/bash
# Cortex MCP 启动脚本 - 自动适配架构

cd "$(dirname "$0")"
source .venv/bin/activate

# 检测当前架构
ARCH=$(uname -m)
echo "检测到系统架构: $ARCH"

# 根据架构启动
if [ "$ARCH" = "arm64" ]; then
    echo "使用 ARM64 模式启动 MCP 服务器"
    exec arch -arm64 python -m cortex_mcp.server "$@"
elif [ "$ARCH" = "x86_64" ]; then
    echo "使用 x86_64 模式启动 MCP 服务器"
    # 如果 pydantic_core 架构不匹配，需要重新安装
    if ! python -c "import pydantic_core" 2>/dev/null; then
        echo ""
        echo "检测到 pydantic_core 架构不匹配，正在重新安装..."
        pip uninstall -y pydantic-core && pip install pydantic-core
        echo "重新安装完成"
    fi
    exec python -m cortex_mcp.server "$@"
else
    echo "未知架构: $ARCH"
    exit 1
fi
