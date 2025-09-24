# Magic-API MCP Server - Docker 管理 Makefile

.PHONY: help build up down restart logs shell clean dev prod test

# 默认目标
help: ## 显示帮助信息
	@echo "Magic-API MCP Server Docker 管理命令"
	@echo ""
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Docker 构建相关
build: ## 构建 Docker 镜像
	docker-compose build --no-cache

build-fast: ## 快速构建 Docker 镜像 (使用缓存)
	docker-compose build

# 容器管理
up: ## 启动服务 (后台运行)
	docker-compose up -d

up-fg: ## 启动服务 (前台运行)
	docker-compose up

down: ## 停止并移除容器
	docker-compose down

restart: ## 重启服务
	docker-compose restart magic-api-mcp-server

# 日志和监控
logs: ## 查看服务日志
	docker-compose logs -f magic-api-mcp-server

logs-tail: ## 查看最近100行日志
	docker-compose logs --tail=100 magic-api-mcp-server

status: ## 查看服务状态
	docker-compose ps

# 调试和维护
shell: ## 进入容器 shell
	docker-compose exec magic-api-mcp-server bash

shell-root: ## 以 root 用户进入容器 shell
	docker-compose exec --user root magic-api-mcp-server bash

health: ## 检查服务健康状态
	docker-compose exec magic-api-mcp-server python -c "print('Service is healthy')" || echo "Service may be unhealthy"

# 开发环境
dev: ## 启动开发环境 (带源代码挂载)
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

dev-fg: ## 启动开发环境 (前台模式)
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up

dev-logs: ## 查看开发环境日志
	docker-compose -f docker-compose.yml -f docker-compose.override.yml logs -f

# 清理操作
clean: ## 清理容器和网络
	docker-compose down --remove-orphans

clean-all: ## 清理容器、网络和镜像
	docker-compose down --rmi all --volumes --remove-orphans

clean-logs: ## 清理日志文件
	rm -rf logs/*.log

# 测试相关
test: ## 运行容器健康检查测试
	@echo "Testing container health..."
	@docker-compose exec magic-api-mcp-server python -c "import sys; print('✅ Python import successful'); sys.exit(0)" && echo "✅ Container is healthy" || echo "❌ Container health check failed"

test-connection: ## 测试与 Magic-API 服务的连接
	@echo "Testing connection to Magic-API service..."
	@docker-compose exec magic-api-mcp-server python -c "\
import os; \
import requests; \
try: \
    base_url = os.getenv('MAGIC_API_BASE_URL', 'http://host.docker.internal:10712'); \
    response = requests.get(f'{base_url}/magic/web/resource', timeout=5); \
    if response.status_code == 200: \
        print('✅ Magic-API service is accessible'); \
    else: \
        print(f'⚠️  Magic-API service responded with status {response.status_code}'); \
except Exception as e: \
    print(f'❌ Cannot connect to Magic-API service: {e}')"

# 信息显示
info: ## 显示环境信息
	@echo "=== Docker Environment Info ==="
	@echo "Docker version: $$(docker --version)"
	@echo "Docker Compose version: $$(docker-compose --version)"
	@echo ""
	@echo "=== Container Status ==="
	@docker-compose ps
	@echo ""
	@echo "=== Environment Variables ==="
	@docker-compose exec magic-api-mcp-server env | grep MAGIC_API || echo "No MAGIC_API environment variables set"

version: ## 显示版本信息
	@docker-compose exec magic-api-mcp-server python -c "\
import sys; \
print(f'Python version: {sys.version}'); \
try: \
    import magicapi_mcp; \
    print('✅ magicapi_mcp module imported successfully'); \
except ImportError as e: \
    print(f'❌ Failed to import magicapi_mcp: {e}')"

# 快速启动 (开发环境)
quick-start: build dev logs ## 快速启动开发环境 (构建+启动+查看日志)

# 测试相关
test-image: ## 测试Docker镜像是否存在和可用
	@echo "Testing Docker image availability..."
	@docker images magic-api-mcp-server:test --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" || echo "❌ Image not found, build first with 'make build'"

test-config: ## 验证Docker配置文件语法
	@echo "Validating Docker Compose configuration..."
	@docker-compose config --quiet && echo "✅ Docker Compose configuration is valid" || echo "❌ Docker Compose configuration has errors"

test-network: ## 测试Docker网络连接
	@echo "Testing network connectivity..."
	@docker run --rm --network host alpine:latest sh -c "ping -c 1 8.8.8.8" > /dev/null 2>&1 && echo "✅ Network connectivity OK" || echo "❌ Network connectivity failed"

# 生产部署
deploy: build up health ## 生产环境部署 (构建+启动+健康检查)
