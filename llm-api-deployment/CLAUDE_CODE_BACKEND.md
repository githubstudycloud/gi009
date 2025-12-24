# Claude Code 本地模型集成指南

本指南介绍如何将本地部署的开源大模型作为 Claude Code 的运行引擎，替代 Anthropic Claude API。

## 方案概述

将本地模型作为 Claude Code 的后端有两种方式：

### 方案一：使用 LiteLLM 代理（推荐）⭐

通过 LiteLLM 将本地模型包装成 Claude API 兼容接口，Claude Code 直接调用本地服务。

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Claude Code │ ───> │   LiteLLM    │ ───> │  本地 vLLM   │
│              │      │  (API 代理)  │      │    模型      │
└──────────────┘      └──────────────┘      └──────────────┘
```

### 方案二：使用路由转发

通过修改 hosts 或代理，拦截 Claude API 请求转发到本地。

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Claude Code │ ───> │     Proxy    │ ───> │  本地模型    │
│              │      │   (Router)   │      │   + 适配层   │
└──────────────┘      └──────────────┘      └──────────────┘
```

## 方案一：LiteLLM 代理（推荐）

### 1. 启动本地模型

首先启动 vLLM 服务：

```bash
cd llm-api-deployment
docker-compose up -d
```

等待模型加载完成。

### 2. 配置 LiteLLM

已包含在项目中，使用增强配置：

**docker-compose-with-litellm.yml**:
```yaml
version: '3.8'

services:
  # vLLM 服务
  vllm:
    image: vllm/vllm-openai:latest
    container_name: qwen-coder-vllm
    ports:
      - "8000:8000"
    volumes:
      - ./models:/root/.cache/huggingface
    environment:
      - HF_ENDPOINT=https://hf-mirror.com
    command: >
      --model Qwen/Qwen2.5-Coder-32B-Instruct
      --served-model-name qwen2.5-coder-32b
      --host 0.0.0.0
      --port 8000
      --max-model-len 8192
      --max-num-seqs 10
      --trust-remote-code
      --dtype bfloat16
    restart: unless-stopped

  # LiteLLM 代理 - 伪装成 Claude API
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: litellm-claude-proxy
    ports:
      - "8080:8080"
    environment:
      - LITELLM_MASTER_KEY=sk-1234
      - DATABASE_URL=
    volumes:
      - ./litellm-claude-config.yaml:/app/config.yaml
    command: >
      --config /app/config.yaml
      --port 8080
      --host 0.0.0.0
      --detailed_debug
    depends_on:
      - vllm
    restart: unless-stopped

networks:
  default:
    name: claude-local-network
```

**litellm-claude-config.yaml**:
```yaml
model_list:
  # 将本地模型映射为 Claude 模型
  - model_name: claude-3-5-sonnet-20241022
    litellm_params:
      model: openai/qwen2.5-coder-32b
      api_base: http://vllm:8000/v1
      api_key: dummy

  - model_name: claude-sonnet-4-5-20250929
    litellm_params:
      model: openai/qwen2.5-coder-32b
      api_base: http://vllm:8000/v1
      api_key: dummy

  # 也可以映射为 OpenAI 模型供其他用途
  - model_name: gpt-4
    litellm_params:
      model: openai/qwen2.5-coder-32b
      api_base: http://vllm:8000/v1
      api_key: dummy

general_settings:
  master_key: sk-1234567890abcdef  # 修改为你的密钥

litellm_settings:
  drop_params: true
  success_callback: []

router_settings:
  routing_strategy: simple-shuffle
  num_retries: 2
  timeout: 300
```

### 3. 启动完整服务

```bash
cd llm-api-deployment

# 启动 vLLM + LiteLLM
docker-compose -f docker-compose-with-litellm.yml up -d

# 查看日志
docker-compose -f docker-compose-with-litellm.yml logs -f
```

### 4. 测试代理

```bash
# 测试 Claude API 格式请求
curl http://localhost:8080/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk-1234567890abcdef" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "你好，请用中文介绍你自己"}
    ]
  }'
```

### 5. 配置 Claude Code

#### 方式 A：环境变量（推荐）

```bash
# 设置 Claude Code 使用本地 API
export ANTHROPIC_API_KEY="sk-1234567890abcdef"
export ANTHROPIC_BASE_URL="http://localhost:8080"

# 或者在 ~/.bashrc 或 ~/.zshrc 中添加
echo 'export ANTHROPIC_API_KEY="sk-1234567890abcdef"' >> ~/.bashrc
echo 'export ANTHROPIC_BASE_URL="http://localhost:8080"' >> ~/.bashrc
```

#### 方式 B：Claude Code 配置文件

编辑 Claude Code 配置文件（如果支持）：

```json
{
  "api": {
    "anthropic": {
      "apiKey": "sk-1234567890abcdef",
      "baseUrl": "http://localhost:8080"
    }
  }
}
```

#### 方式 C：启动时指定

```bash
claude-code --api-key sk-1234567890abcdef --api-base http://localhost:8080
```

### 6. 验证集成

启动 Claude Code 后，它会自动使用本地模型：

```bash
# 启动 Claude Code
claude-code

# 测试对话
> 你好，请介绍一下你自己

# 查看 LiteLLM 日志确认请求
docker logs -f litellm-claude-proxy
```

## 方案二：Nginx 代理路由

如果 Claude Code 不支持自定义 API endpoint，使用 Nginx 拦截请求。

### 1. Nginx 配置

**nginx.conf**:
```nginx
http {
    upstream local_model {
        server localhost:8080;
    }

    server {
        listen 443 ssl;
        server_name api.anthropic.com;

        # 自签名证书（开发用）
        ssl_certificate /etc/nginx/certs/cert.pem;
        ssl_certificate_key /etc/nginx/certs/key.pem;

        location / {
            proxy_pass http://local_model;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_read_timeout 300s;
        }
    }
}
```

### 2. 修改 hosts

```bash
# 编辑 hosts 文件
sudo nano /etc/hosts

# 添加
127.0.0.1 api.anthropic.com
```

### 3. 生成自签名证书

```bash
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes
```

### 4. 启动 Nginx

```bash
docker run -d \
  --name nginx-claude-proxy \
  -p 443:443 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf \
  -v $(pwd)/certs:/etc/nginx/certs \
  nginx:alpine
```

## 方案三：使用 mitmproxy（开发调试）

用于开发调试，拦截并查看 API 请求。

### 1. 安装 mitmproxy

```bash
pip install mitmproxy
```

### 2. 创建拦截脚本

**anthropic_proxy.py**:
```python
from mitmproxy import http
import requests
import json

LOCAL_API = "http://localhost:8080"

def request(flow: http.HTTPFlow) -> None:
    # 拦截 Anthropic API 请求
    if "api.anthropic.com" in flow.request.pretty_host:
        # 转换请求到本地 API
        flow.request.host = "localhost"
        flow.request.port = 8080
        flow.request.scheme = "http"

        print(f"拦截请求: {flow.request.path}")
        print(f"转发到: {LOCAL_API}")
```

### 3. 启动代理

```bash
mitmdump -s anthropic_proxy.py --listen-port 8888
```

### 4. 配置 Claude Code 使用代理

```bash
export HTTP_PROXY=http://localhost:8888
export HTTPS_PROXY=http://localhost:8888
```

## 性能优化建议

### 1. 使用更快的模型

对于 Claude Code 实时使用，建议：

```yaml
# 使用 DeepSeek-Coder-V2-Lite（更快）
--model deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct
```

### 2. 调整参数

```yaml
# 优化响应速度
--max-model-len 4096        # 减小上下文
--max-num-seqs 5            # 减少并发
--enable-chunked-prefill    # 启用分块
```

### 3. 启用缓存

在 LiteLLM 配置中：

```yaml
litellm_settings:
  cache: true
  cache_params:
    type: redis
    host: localhost
    port: 6379
```

## 故障排查

### 问题 1：Claude Code 仍然访问远程 API

检查环境变量：

```bash
echo $ANTHROPIC_BASE_URL
echo $ANTHROPIC_API_KEY

# 查看 Claude Code 实际使用的 endpoint
claude-code --verbose
```

### 问题 2：API 格式不兼容

查看 LiteLLM 日志：

```bash
docker logs -f litellm-claude-proxy
```

确保请求格式正确。

### 问题 3：响应速度慢

```bash
# 检查模型加载状态
docker logs vllm

# 监控资源使用
docker stats
```

考虑使用更小/更快的模型。

## 验证清单

- [ ] vLLM 服务正常运行
- [ ] LiteLLM 代理正常启动
- [ ] 可以通过 curl 测试 Claude API 格式请求
- [ ] Claude Code 环境变量正确设置
- [ ] Claude Code 请求被正确拦截并转发
- [ ] 响应速度可接受（< 30秒）

## 预期性能

### Qwen2.5-Coder-32B (E5-2680)

- **首次响应**: 2-4秒
- **生成速度**: 8-12 tokens/秒
- **代码生成**: 适合实时使用
- **并发用户**: 3-5人

### DeepSeek-Coder-V2-Lite

- **首次响应**: 1-2秒
- **生成速度**: 12-18 tokens/秒
- **代码生成**: 实时体验更好
- **并发用户**: 5-8人

## 下一步

1. 根据你的网络环境选择合适的方案
2. 测试并验证集成
3. 根据实际性能调整模型和参数
4. 考虑添加监控和日志

## 相关文档

- [部署指南](./DEPLOYMENT.md)
- [API 文档](./API.md)
- [模型对比](./MODEL_COMPARISON.md)
- [故障排查](./TROUBLESHOOTING.md)
