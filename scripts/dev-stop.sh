#!/bin/bash

# 一键停止前后端脚本

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}    Cortex 前后端停止脚本${NC}"
echo -e "${BLUE}======================================${NC}"

# 检查进程文件
if [ ! -f "$PROJECT_ROOT/.pids" ]; then
    echo -e "${YELLOW}未找到进程文件 .pids${NC}"
    echo -e "${YELLOW}尝试查找进程...${NC}"

    # 尝试通过进程名查找
    BACKEND_PIDS=$(pgrep -f "uvicorn app.main:app" || true)
    FRONTEND_PIDS=$(pgrep -f "vite.*cortex-frontend" || true)

    if [ -z "$BACKEND_PIDS" ] && [ -z "$FRONTEND_PIDS" ]; then
        echo -e "${GREEN}未发现运行中的服务${NC}"
        exit 0
    fi

    if [ -n "$BACKEND_PIDS" ]; then
        echo -e "${YELLOW}发现后端进程: $BACKEND_PIDS${NC}"
        echo -e "$BACKEND_PIDS" | xargs kill 2>/dev/null || true
        echo -e "${GREEN}后端已停止${NC}"
    fi

    if [ -n "$FRONTEND_PIDS" ]; then
        echo -e "${YELLOW}发现前端进程: $FRONTEND_PIDS${NC}"
        echo -e "$FRONTEND_PIDS" | xargs kill 2>/dev/null || true
        echo -e "${GREEN}前端已停止${NC}"
    fi

    exit 0
fi

# 读取进程ID
PIDS=($(cat "$PROJECT_ROOT/.pids"))

if [ ${#PIDS[@]} -ge 1 ]; then
    BACKEND_PID=${PIDS[0]}
    FRONTEND_PID=${PIDS[1]}

    # 停止后端
    echo -e "${GREEN}[1/2] 停止后端服务...${NC}"
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}后端已停止 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}后端进程不存在 (PID: $BACKEND_PID)${NC}"
    fi
fi

if [ ${#PIDS[@]} -ge 2 ]; then
    # 停止前端
    echo -e "${GREEN}[2/2] 停止前端服务...${NC}"
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}前端已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}前端进程不存在 (PID: $FRONTEND_PID)${NC}"
    fi
fi

# 删除进程文件
rm -f "$PROJECT_ROOT/.pids"

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✓ 所有服务已停止${NC}"
echo -e "${BLUE}======================================${NC}"
