# 部署指南

## 系统要求

### 硬件要求

| 配置项 | 最低要求 | 推荐配置 |
|--------|---------|---------|
| CPU | 8核 | 16核以上 |
| 内存 | 32GB | 64GB以上 |
| 磁盘 | 100GB | 200GB以上 SSD |
| 网络 | 100Mbps | 1Gbps |

### 软件要求

- Ubuntu 18.04 或更高版本
- Docker 20.10 或更高版本
- Docker Compose 1.29 或更高版本
- 可选：NVIDIA Docker（如果使用 GPU）


## 安装步骤

### 1. 安装 Docker

```bash
# 更新包索引
sudo apt-get update

# 安装必要的软件包
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 设置稳定版仓库
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组（可选）
sudo usermod -aG docker $USER
```

### 2. 安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 3. 克隆项目

```bash
git clone https://github.com/githubstudycloud/gi009.git
cd gi009
```

### 4. 配置环境（可选）

创建 `.env` 文件配置环境变量：

```bash
# Hugging Face Token（可选，用于下载受限模型）
HF_TOKEN=your_huggingface_token_here

# API端口
API_PORT=8000

# 日志级别
LOG_LEVEL=INFO
```

### 5. 选择模型配置

根据你的内存大小选择合适的配置：

#### 方案A：Qwen2.5-Coder-32B（推荐，50GB内存）

```bash
docker-compose up -d
```

#### 方案B：DeepSeek-Coder-V2-Lite（30GB内存）

```bash
docker-compose -f docker-compose-deepseek.yml up -d
```

#### 方案C：Qwen2.5-72B（100GB内存）

```bash
docker-compose -f docker-compose-qwen72b.yml up -d
```

#### 方案D：Ollama 部署（简单易用）

```bash
docker-compose -f docker-compose-ollama.yml up -d

# 等待 Ollama 启动后，拉取模型
docker exec -it qwen-coder-ollama ollama pull qwen2.5-coder:32b
```

### 6. 查看启动日志

```bash
docker-compose logs -f
```

首次启动会下载模型，可能需要 15-30 分钟，请耐心等待。

### 7. 验证部署

等待模型加载完成后，测试 API：

```bash
# 检查健康状态
curl http://localhost:8000/health

# 列出模型
curl http://localhost:8000/v1/models

# 测试对话
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'
```

或使用测试脚本：

```bash
chmod +x test-api.sh
./test-api.sh
```


## 使用 Hugging Face 镜像加速下载

如果你在中国大陆，可以使用镜像加速模型下载：

### 方法1：环境变量（已在 docker-compose.yml 中配置）

```yaml
environment:
  - HF_ENDPOINT=https://hf-mirror.com
```

### 方法2：手动下载模型

```bash
# 使用 git clone 下载模型
cd models
export HF_ENDPOINT=https://hf-mirror.com
git clone https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct

# 修改 docker-compose.yml 使用本地模型
# 将 --model Qwen/Qwen2.5-Coder-32B-Instruct
# 改为 --model /root/.cache/huggingface/Qwen2.5-Coder-32B-Instruct
```


## 性能调优

### 调整并发数

在 `docker-compose.yml` 中修改：

```yaml
command: >
  ...
  --max-num-seqs 10    # 同时处理的请求数（1-10用户建议10-20）
  --max-model-len 8192 # 上下文长度（越大越消耗内存）
```

### 内存优化

1. **使用量化模型**：减少 40-50% 内存使用

```yaml
# 在 command 中添加
--quantization awq  # 或 gptq
```

2. **减少上下文长度**：

```yaml
--max-model-len 4096  # 从 8192 减少到 4096
```

3. **启用内存交换**（不推荐，会降低性能）：

```yaml
--swap-space 4  # 单位：GB
```

### CPU 优化

```bash
# 设置 CPU 亲和性
docker-compose up -d
docker update --cpuset-cpus="0-15" qwen-coder-32b-vllm
```


## 监控与日志

### 查看实时日志

```bash
docker-compose logs -f
```

### 查看资源使用

```bash
docker stats
```

### 日志文件位置

```
./logs/
├── vllm.log
└── error.log
```


## 常见问题排查

### 1. 内存不足 (OOM)

**症状**：容器重启，日志显示 "Out of Memory"

**解决方案**：
- 使用更小的模型
- 减少 `--max-num-seqs`
- 减少 `--max-model-len`
- 启用量化

### 2. 模型下载失败

**症状**：无法连接到 Hugging Face

**解决方案**：
```bash
# 使用镜像
export HF_ENDPOINT=https://hf-mirror.com

# 或手动下载后挂载本地目录
```

### 3. 端口冲突

**症状**：`bind: address already in use`

**解决方案**：
```bash
# 修改 docker-compose.yml 中的端口
ports:
  - "8001:8000"  # 改为其他端口
```

### 4. Function Calling 不工作

**症状**：模型不调用工具

**解决方案**：
- 确保使用支持工具调用的模型（Qwen2.5、DeepSeek-V2）
- 检查请求格式是否正确
- 使用最新版本的 vLLM

### 5. 响应速度慢

**症状**：请求响应时间长

**解决方案**：
- 减少 `max_tokens`
- 使用更小的模型
- 增加 CPU 核心数
- 检查是否有内存交换


## 升级与维护

### 更新 Docker 镜像

```bash
docker-compose pull
docker-compose up -d
```

### 备份模型

```bash
tar -czf models-backup.tar.gz models/
```

### 清理磁盘空间

```bash
# 清理未使用的 Docker 资源
docker system prune -a

# 清理模型缓存
rm -rf models/hub/*
```


## 安全建议

1. **不要将服务直接暴露到公网**：使用反向代理（Nginx、Traefik）
2. **启用认证**：使用 API Key 或 OAuth
3. **限流**：防止滥用
4. **HTTPS**：使用 SSL/TLS 加密通信
5. **定期更新**：及时更新 Docker 镜像和系统


## 生产环境建议

### 使用 Nginx 反向代理

```nginx
upstream llm_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://llm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

### 使用进程管理器

```bash
# 安装 systemd 服务
sudo tee /etc/systemd/system/llm-api.service > /dev/null <<EOF
[Unit]
Description=LLM API Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/gi009
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable llm-api
sudo systemctl start llm-api
```


## 下一步

- 阅读 [API使用指南](./API.md)
- 查看 [Claude Code 集成](./CLAUDE_CODE_INTEGRATION.md)
- 运行性能测试：`python3 benchmark.py`
