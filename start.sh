#!/bin/bash

# 快速启动脚本

set -e

echo "========================================"
echo "  LLM API 快速启动脚本"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker 和 Docker Compose 已安装${NC}"
echo ""

# 选择部署方案
echo "请选择部署方案："
echo "1. Qwen2.5-Coder-32B (推荐, 50GB内存)"
echo "2. DeepSeek-Coder-V2-Lite (30GB内存)"
echo "3. Qwen2.5-72B (100GB内存)"
echo "4. Ollama (简单易用)"
echo ""

read -p "请输入选项 (1-4) [默认: 1]: " choice
choice=${choice:-1}

case $choice in
    1)
        COMPOSE_FILE="docker-compose.yml"
        MODEL_NAME="Qwen2.5-Coder-32B"
        ;;
    2)
        COMPOSE_FILE="docker-compose-deepseek.yml"
        MODEL_NAME="DeepSeek-Coder-V2-Lite"
        ;;
    3)
        COMPOSE_FILE="docker-compose-qwen72b.yml"
        MODEL_NAME="Qwen2.5-72B"
        ;;
    4)
        COMPOSE_FILE="docker-compose-ollama.yml"
        MODEL_NAME="Ollama"
        ;;
    *)
        echo -e "${RED}无效选项，使用默认方案${NC}"
        COMPOSE_FILE="docker-compose.yml"
        MODEL_NAME="Qwen2.5-Coder-32B"
        ;;
esac

echo ""
echo -e "${GREEN}已选择: $MODEL_NAME${NC}"
echo ""

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p models logs

# 检查是否需要停止现有服务
if docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}检测到正在运行的服务${NC}"
    read -p "是否停止并重新启动? (y/N): " restart
    if [[ $restart =~ ^[Yy]$ ]]; then
        echo "停止现有服务..."
        docker-compose down
    else
        echo "取消启动"
        exit 0
    fi
fi

# 启动服务
echo ""
echo -e "${GREEN}启动服务...${NC}"
echo "使用配置文件: $COMPOSE_FILE"
echo ""

docker-compose -f "$COMPOSE_FILE" up -d

echo ""
echo -e "${GREEN}服务启动成功！${NC}"
echo ""
echo "========================================"
echo "  重要信息"
echo "========================================"
echo ""
echo "API 地址: http://localhost:8000"
echo "健康检查: http://localhost:8000/health"
echo ""
echo "首次启动需要下载模型，可能需要 15-30 分钟"
echo ""
echo "查看日志："
echo "  docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "停止服务："
echo "  docker-compose -f $COMPOSE_FILE down"
echo ""
echo "测试 API："
echo "  ./test-api.sh"
echo ""
echo "========================================"

# 询问是否查看日志
read -p "是否查看实时日志? (Y/n): " view_logs
view_logs=${view_logs:-Y}

if [[ $view_logs =~ ^[Yy]$ ]]; then
    echo ""
    echo "按 Ctrl+C 退出日志查看"
    sleep 2
    docker-compose -f "$COMPOSE_FILE" logs -f
fi
