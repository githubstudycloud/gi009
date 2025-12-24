# 快速开始指南

欢迎使用开源大模型部署方案！本指南将帮助你在 5 分钟内部署一个支持 Claude Code 工具调用的本地大模型。


## 前提条件

- Ubuntu 18.04 或更高版本
- 至少 32GB 内存（推荐 64GB+）
- Docker 和 Docker Compose 已安装


## 快速部署（3 步）

### 1. 克隆仓库

```bash
git clone https://github.com/githubstudycloud/gi009.git
cd gi009
```

### 2. 启动服务

**方式A：使用启动脚本（推荐）**

```bash
chmod +x start.sh
./start.sh
```

脚本会引导你选择合适的模型并自动启动服务。

**方式B：手动启动**

```bash
# 方案1: Qwen2.5-Coder-32B (推荐)
docker-compose up -d

# 方案2: DeepSeek-Coder-V2-Lite (省内存)
docker-compose -f docker-compose-deepseek.yml up -d

# 方案3: Qwen2.5-72B (更强性能)
docker-compose -f docker-compose-qwen72b.yml up -d
```

### 3. 等待模型加载

首次启动会自动下载模型，需要 15-30 分钟。查看进度：

```bash
docker-compose logs -f
```

当看到 "Application startup complete" 时，表示服务已就绪。


## 验证部署

### 测试 API

```bash
# 健康检查
curl http://localhost:8000/health

# 测试对话
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'
```

### 使用测试脚本

```bash
chmod +x test-api.sh
./test-api.sh
```

### 运行性能测试

```bash
pip3 install aiohttp
python3 benchmark.py
```


## 模型选择指南

### 推荐配置

| 内存大小 | 推荐模型 | 特点 |
|---------|---------|------|
| 32-50GB | DeepSeek-Coder-V2-Lite | 省资源，代码能力强 |
| 50-70GB | **Qwen2.5-Coder-32B** | **最佳平衡（推荐）** |
| 70-100GB | Qwen2.5-72B | 最强性能 |

### 详细对比

#### Qwen2.5-Coder-32B ⭐ 推荐

```bash
docker-compose up -d
```

- **内存占用**: 40-50GB
- **代码能力**: ⭐⭐⭐⭐⭐
- **中文支持**: ⭐⭐⭐⭐⭐
- **响应速度**: ⭐⭐⭐⭐
- **工具调用**: ✅ 原生支持
- **适用场景**: 代码生成、API 调用、文档编写

#### DeepSeek-Coder-V2-Lite

```bash
docker-compose -f docker-compose-deepseek.yml up -d
```

- **内存占用**: 20-30GB
- **代码能力**: ⭐⭐⭐⭐
- **中文支持**: ⭐⭐⭐⭐
- **响应速度**: ⭐⭐⭐⭐⭐
- **工具调用**: ✅ 支持
- **适用场景**: 资源受限环境、快速响应

#### Qwen2.5-72B

```bash
docker-compose -f docker-compose-qwen72b.yml up -d
```

- **内存占用**: 80-100GB
- **代码能力**: ⭐⭐⭐⭐⭐
- **中文支持**: ⭐⭐⭐⭐⭐
- **响应速度**: ⭐⭐⭐
- **工具调用**: ✅ 原生支持
- **适用场景**: 复杂推理、高质量代码生成


## 集成 Claude Code

### 方法 1：使用 MCP 服务器

```bash
# 安装 MCP OpenAI 服务器
npm install -g @modelcontextprotocol/server-openai

# 配置 Claude Code
# 编辑 ~/.config/claude-code/config.json
```

添加配置：

```json
{
  "mcpServers": {
    "local-llm": {
      "command": "mcp-server-openai",
      "env": {
        "OPENAI_API_KEY": "dummy",
        "OPENAI_BASE_URL": "http://localhost:8000/v1"
      }
    }
  }
}
```

详细集成指南请查看 [CLAUDE_CODE_INTEGRATION.md](./CLAUDE_CODE_INTEGRATION.md)


## 常用命令

### 查看日志

```bash
docker-compose logs -f
```

### 查看状态

```bash
docker-compose ps
docker stats
```

### 重启服务

```bash
docker-compose restart
```

### 停止服务

```bash
docker-compose down
```

### 更新服务

```bash
docker-compose pull
docker-compose up -d
```


## 性能调优

### 调整并发数

编辑 `docker-compose.yml`：

```yaml
command: >
  ...
  --max-num-seqs 10    # 10个用户建议设为10-20
```

### 调整上下文长度

```yaml
--max-model-len 8192   # 减少可降低内存占用
```

### 查看资源使用

```bash
docker stats --no-stream
```


## 故障排查

### 问题 1：内存不足

**症状**：容器频繁重启

**解决**：
```bash
# 使用更小的模型
docker-compose -f docker-compose-deepseek.yml up -d

# 或减少并发数
# 编辑 docker-compose.yml，减少 --max-num-seqs
```

### 问题 2：模型下载慢

**症状**：长时间停在下载界面

**解决**：使用 HF 镜像（已在配置中启用）
```yaml
environment:
  - HF_ENDPOINT=https://hf-mirror.com
```

### 问题 3：端口被占用

**症状**：`address already in use`

**解决**：修改端口
```yaml
ports:
  - "8001:8000"  # 改为其他端口
```

### 问题 4：API 无响应

**检查**：
```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs --tail=50

# 测试健康检查
curl http://localhost:8000/health
```


## 使用示例

### Python 示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

response = client.chat.completions.create(
    model="qwen2.5-coder-32b-instruct",
    messages=[
        {"role": "user", "content": "写一个Python快速排序"}
    ]
)

print(response.choices[0].message.content)
```

### curl 示例

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [
      {"role": "system", "content": "你是一个专业的编程助手"},
      {"role": "user", "content": "解释什么是Docker"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### Function Calling 示例

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [
      {"role": "user", "content": "帮我搜索快速排序的代码"}
    ],
    "tools": [{
      "type": "function",
      "function": {
        "name": "search_code",
        "description": "搜索代码库",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {"type": "string"}
          },
          "required": ["query"]
        }
      }
    }]
  }'
```


## 下一步

- 📖 [完整部署指南](./DEPLOYMENT.md)
- 🔌 [API 使用文档](./API.md)
- 🤖 [Claude Code 集成](./CLAUDE_CODE_INTEGRATION.md)
- ⚡ [性能测试](./benchmark.py)


## 获取帮助

- 查看日志：`docker-compose logs -f`
- 查看文档：浏览本仓库的 Markdown 文件
- 提交问题：https://github.com/githubstudycloud/gi009/issues


## 常见问题

**Q: 需要 GPU 吗？**
A: 不需要，本方案使用 CPU 推理。

**Q: 能支持多少用户？**
A: 推荐配置可支持 5-10 个用户同时使用。

**Q: 响应速度如何？**
A: CPU 推理速度约为 5-15 tokens/秒，取决于 CPU 性能。

**Q: 支持哪些语言？**
A: 支持中文、英文等多种语言，中文支持特别好。

**Q: 如何更新模型？**
A: `docker-compose pull && docker-compose up -d`


## 许可证

MIT License
