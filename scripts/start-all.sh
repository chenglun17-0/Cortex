#!/bin/bash

# 一键启动前后端脚本

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}    Cortex 前后端启动脚本${NC}"
echo -e "${BLUE}======================================${NC}"

# 检查是否已经启动
if [ -f "$PROJECT_ROOT/.pids" ]; then
    echo -e "${YELLOW}检测到进程文件 .pids，请先运行停止脚本${NC}"
    exit 1
fi

# 创建日志目录
mkdir -p "$PROJECT_ROOT/logs"

# 启动后端
echo -e "${GREEN}[1/2] 启动后端服务...${NC}"
cd "$PROJECT_ROOT/cortex-backend"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${RED}错误: 后端虚拟环境不存在，请先安装依赖${NC}"
    echo -e "${YELLOW}运行: cd cortex-backend && python3 -m venv .venv && source .venv/bin/activate && pip install -e .${NC}"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: 未找到 .env 文件${NC}"
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}复制 .env.example 到 .env${NC}"
        cp .env.example .env
    else
        echo -e "${RED}错误: 请创建 .env 文件${NC}"
        exit 1
    fi
fi

# 激活虚拟环境并启动后端
source .venv/bin/activate
nohup uvicorn app.main:app --reload > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
BACKEND_PID=$!
deactivate

echo -e "${GREEN}后端已启动 (PID: $BACKEND_PID)${NC}"

# 等待后端启动
sleep 5

# 检查后端是否启动成功
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${RED}后端启动失败，请查看日志: tail -f $PROJECT_ROOT/logs/backend.log${NC}"
    exit 1
fi

echo -e "${YELLOW}日志文件: $PROJECT_ROOT/logs/backend.log${NC}"

# 启动前端
echo -e "${GREEN}[2/2] 启动前端服务...${NC}"
cd "$PROJECT_ROOT/cortex-frontend"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${RED}错误: 前端依赖未安装，请先运行 npm install${NC}"
    kill $BACKEND_PID 2>/dev/null
    rm -f "$PROJECT_ROOT/.pids"
    exit 1
fi

nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}前端已启动 (PID: $FRONTEND_PID)${NC}"

# 等待前端启动
sleep 3

# 检查前端是否启动成功
if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo -e "${RED}前端启动失败，请查看日志: tail -f $PROJECT_ROOT/logs/frontend.log${NC}"
    kill $BACKEND_PID 2>/dev/null
    rm -f "$PROJECT_ROOT/.pids"
    exit 1
fi

echo -e "${YELLOW}日志文件: $PROJECT_ROOT/logs/frontend.log${NC}"

# 保存进程ID
echo "$BACKEND_PID" > "$PROJECT_ROOT/.pids"
echo "$FRONTEND_PID" >> "$PROJECT_ROOT/.pids"

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✓ 所有服务启动成功！${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}后端服务: http://localhost:8000${NC}"
echo -e "${GREEN}前端服务: http://localhost:5173${NC}"
echo -e "${YELLOW}停止服务: ./scripts/stop-all.sh${NC}"
echo -e "${YELLOW}查看日志: tail -f logs/backend.log 或 tail -f logs/frontend.log${NC}"
echo -e "${BLUE}======================================${NC}"
