#!/bin/bash

# Cortex 项目部署脚本（在服务器上执行）
# 用法: ./scripts/deploy.sh

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}    Cortex 项目部署脚本${NC}"
echo -e "${BLUE}======================================${NC}"

# 项目目录
PROJECT_DIR="$HOME/Cortex"
cd "$PROJECT_DIR"

echo -e "${GREEN}[1/4] 更新代码...${NC}"
git pull origin main

echo -e "${GREEN}[2/4] 检查 .env 配置...${NC}"

ENV_FILE="$PROJECT_DIR/cortex-backend/.env"

if [ -f "$ENV_FILE" ]; then
    if grep -q "your-password\|your-secret-key\|your_api_key" "$ENV_FILE" 2>/dev/null; then
        echo -e "${RED}错误: .env 文件中还有占位符未替换！${NC}"
        echo "需要修改: your_password, your-secret-key, api keys 等"
        exit 1
    fi
else
    echo -e "${RED}错误: .env 文件不存在！${NC}"
    echo "请创建: $ENV_FILE"
    exit 1
fi

echo -e "${GREEN}[3/4] 停止旧容器...${NC}"
docker-compose down 2>/dev/null || true

echo -e "${GREEN}[4/4] 启动服务...${NC}"
docker-compose up -d --build

echo ""
echo "服务状态:"
docker-compose ps

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}======================================${NC}"
