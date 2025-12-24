#!/bin/bash

# Claude Code 本地模型后端快速启动脚本

set -e

echo "========================================"
echo "  Claude Code 本地模型后端部署"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker 和 Docker Compose 已安装${NC}"
echo ""

echo -e "${BLUE}本脚本将部署：${NC}"
echo "1. vLLM 推理引擎（Qwen2.5-Coder-32B）"
echo "2. LiteLLM 代理（包装为 Claude API）"
echo ""
echo "部署完成后，Claude Code 可以使用本地模型替代 Anthropic API"
echo ""

read -p "是否继续？(Y/n): " confirm
confirm=${confirm:-Y}

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "取消部署"
    exit 0
fi

# 创建必要的目录
echo ""
echo "创建目录..."
mkdir -p models logs

# 生成随机 API Key
API_KEY="sk-local-$(openssl rand -hex 16)"
echo ""
echo -e "${GREEN}生成 API Key: $API_KEY${NC}"
echo ""

# 创建 .env 文件
cat > .env <<EOF
# LiteLLM API Key
LITELLM_KEY=$API_KEY

# Hugging Face Token (可选)
# HF_TOKEN=your_token_here
EOF

echo "已创建 .env 文件"
echo ""

# 检查是否需要停止现有服务
if docker-compose -f docker-compose-with-litellm.yml ps | grep -q "Up"; then
    echo -e "${YELLOW}检测到正在运行的服务${NC}"
    read -p "是否停止并重新启动? (y/N): " restart
    if [[ $restart =~ ^[Yy]$ ]]; then
        echo "停止现有服务..."
        docker-compose -f docker-compose-with-litellm.yml down
    else
        echo "取消启动"
        exit 0
    fi
fi

# 启动服务
echo ""
echo -e "${GREEN}启动服务...${NC}"
docker-compose -f docker-compose-with-litellm.yml up -d

echo ""
echo -e "${GREEN}服务启动成功！${NC}"
echo ""
echo "========================================"
echo "  配置 Claude Code"
echo "========================================"
echo ""
echo "将以下环境变量添加到你的 shell 配置文件："
echo ""
echo -e "${YELLOW}export ANTHROPIC_API_KEY=\"$API_KEY\"${NC}"
echo -e "${YELLOW}export ANTHROPIC_BASE_URL=\"http://localhost:8080\"${NC}"
echo ""
echo "对于 bash，添加到 ~/.bashrc:"
echo "  echo 'export ANTHROPIC_API_KEY=\"$API_KEY\"' >> ~/.bashrc"
echo "  echo 'export ANTHROPIC_BASE_URL=\"http://localhost:8080\"' >> ~/.bashrc"
echo "  source ~/.bashrc"
echo ""
echo "对于 zsh，添加到 ~/.zshrc:"
echo "  echo 'export ANTHROPIC_API_KEY=\"$API_KEY\"' >> ~/.zshrc"
echo "  echo 'export ANTHROPIC_BASE_URL=\"http://localhost:8080\"' >> ~/.zshrc"
echo "  source ~/.zshrc"
echo ""
echo "========================================"
echo "  测试部署"
echo "========================================"
echo ""
echo "首次启动需要下载模型，可能需要 15-30 分钟"
echo ""
echo "查看日志："
echo "  docker-compose -f docker-compose-with-litellm.yml logs -f"
echo ""
echo "测试 API："
echo "  chmod +x test-claude-api.sh"
echo "  API_KEY=$API_KEY ./test-claude-api.sh"
echo ""
echo "========================================"

# 询问是否查看日志
read -p "是否查看实时日志? (Y/n): " view_logs
view_logs=${view_logs:-Y}

if [[ $view_logs =~ ^[Yy]$ ]]; then
    echo ""
    echo "按 Ctrl+C 退出日志查看"
    sleep 2
    docker-compose -f docker-compose-with-litellm.yml logs -f
fi
