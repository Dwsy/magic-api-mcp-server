# 使用官方 uv Docker 镜像作为基础镜像
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd --create-home --shell /bin/bash mcp-user
USER mcp-user

# 设置工作目录
WORKDIR /home/mcp-user

# 暴露端口 (用于HTTP模式)
EXPOSE 8000

# 设置环境变量默认值
ENV MAGIC_API_BASE_URL=http://host.docker.internal:10712
ENV MAGIC_API_WS_URL=ws://host.docker.internal:10712/magic/web/console
ENV MAGIC_API_TIMEOUT_SECONDS=30.0
ENV LOG_LEVEL=INFO
ENV FASTMCP_TRANSPORT=stdio

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uvx magic-api-mcp-server --help > /dev/null 2>&1 || exit 1

# 启动命令 - 使用 uvx 运行已发布包
CMD ["uvx", "magic-api-mcp-server", "--transport", "stdio"]
