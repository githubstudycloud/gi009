.PHONY: help start stop restart logs status test clean

# 默认目标
help:
	@echo "LLM API 部署管理命令"
	@echo ""
	@echo "使用方法: make [target]"
	@echo ""
	@echo "可用命令:"
	@echo "  start         - 启动服务（默认使用 Qwen2.5-Coder-32B）"
	@echo "  start-deepseek- 启动 DeepSeek-Coder-V2-Lite"
	@echo "  start-qwen72b - 启动 Qwen2.5-72B"
	@echo "  start-ollama  - 启动 Ollama"
	@echo "  stop          - 停止服务"
	@echo "  restart       - 重启服务"
	@echo "  logs          - 查看日志"
	@echo "  status        - 查看服务状态"
	@echo "  test          - 测试 API"
	@echo "  benchmark     - 运行性能测试"
	@echo "  clean         - 清理容器和卷"
	@echo "  pull          - 拉取最新镜像"
	@echo ""

# 启动服务
start:
	@echo "启动 Qwen2.5-Coder-32B..."
	@mkdir -p models logs
	@docker-compose up -d
	@echo "服务已启动！"
	@echo "API: http://localhost:8000"
	@echo "查看日志: make logs"

start-deepseek:
	@echo "启动 DeepSeek-Coder-V2-Lite..."
	@mkdir -p models logs
	@docker-compose -f docker-compose-deepseek.yml up -d
	@echo "服务已启动！"

start-qwen72b:
	@echo "启动 Qwen2.5-72B..."
	@mkdir -p models logs
	@docker-compose -f docker-compose-qwen72b.yml up -d
	@echo "服务已启动！"

start-ollama:
	@echo "启动 Ollama..."
	@mkdir -p ollama-models logs
	@docker-compose -f docker-compose-ollama.yml up -d
	@echo "Ollama 已启动！"
	@echo "拉取模型: docker exec -it qwen-coder-ollama ollama pull qwen2.5-coder:32b"

# 停止服务
stop:
	@echo "停止服务..."
	@docker-compose down || true
	@docker-compose -f docker-compose-deepseek.yml down || true
	@docker-compose -f docker-compose-qwen72b.yml down || true
	@docker-compose -f docker-compose-ollama.yml down || true
	@echo "服务已停止"

# 重启服务
restart:
	@echo "重启服务..."
	@docker-compose restart || true
	@echo "服务已重启"

# 查看日志
logs:
	@docker-compose logs -f

# 查看状态
status:
	@echo "=== Docker 容器状态 ==="
	@docker-compose ps || true
	@echo ""
	@echo "=== 资源使用情况 ==="
	@docker stats --no-stream || true

# 测试 API
test:
	@echo "测试 API..."
	@chmod +x test-api.sh
	@./test-api.sh

# 性能测试
benchmark:
	@echo "运行性能测试..."
	@python3 benchmark.py

# 清理
clean:
	@echo "清理容器和卷..."
	@docker-compose down -v || true
	@docker-compose -f docker-compose-deepseek.yml down -v || true
	@docker-compose -f docker-compose-qwen72b.yml down -v || true
	@docker-compose -f docker-compose-ollama.yml down -v || true
	@echo "清理完成"

# 拉取最新镜像
pull:
	@echo "拉取最新镜像..."
	@docker-compose pull
	@echo "拉取完成"

# 快速健康检查
health:
	@echo "检查服务健康状态..."
	@curl -f http://localhost:8000/health || echo "服务未响应"
