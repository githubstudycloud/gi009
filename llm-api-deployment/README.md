# Claude Code 本地模型后端部署方案

将开源大模型部署为 Claude Code 的本地运行引擎，替代 Anthropic Claude API。

## 核心功能

- 🚀 **完全本地化**: 无需调用远程 API，数据不出内网
- 🔄 **Claude API 兼容**: 通过 LiteLLM 包装，完全兼容 Claude API 格式
- 💻 **CPU 推理**: 无需 GPU，纯内存运行
- 🛠️ **工具调用**: 原生支持 Function Calling
- 🇨🇳 **中文优化**: 代码和文档均支持中文
- 👥 **多用户**: 支持 1-10 人同时使用

## 两种使用方式

### 方式一：作为 Claude Code 后端（推荐）⭐

将本地模型伪装成 Claude API，Claude Code 直接调用本地服务：

```bash
# 一键部署 vLLM + LiteLLM
bash start-claude-backend.sh

# 配置 Claude Code
export ANTHROPIC_API_KEY="your-generated-key"
export ANTHROPIC_BASE_URL="http://localhost:8080"

# Claude Code 现在使用本地模型！
claude-code
```

详细说明：[CLAUDE_CODE_BACKEND.md](./CLAUDE_CODE_BACKEND.md)

### 方式二：作为独立 API 服务

仅部署推理引擎，通过 OpenAI 格式 API 调用：

```bash
# 部署模型
docker-compose up -d

# 通过 API 调用
curl http://localhost:8000/v1/chat/completions ...
```

## 环境信息

- **系统**: Ubuntu 18.04.2+
- **CPU**: Intel Xeon E5-2680（或同等性能）
- **内存**: 363GB 总内存，238GB 可用（最低 32GB）
- **部署方式**: Docker + CPU 推理（纯内存运行）
- **用户数**: 支持 1-10 人同时使用

## 推荐模型方案

### 方案一：Qwen2.5-Coder-32B-Instruct（推荐）⭐

**内存占用**: 约 40-50GB

**优势**:
- 阿里最新代码模型，2024年11月发布
- 原生支持 Function Calling（工具调用）
- 中文和代码能力极强，专为编程任务优化
- 32B参数量，性能与资源平衡最佳
- 支持 128K 上下文
- 兼容 OpenAI API 格式

**适用场景**: 代码生成、文档编写、工具调用


### 方案二：Qwen2.5-72B-Instruct

**内存占用**: 约 80-100GB

**优势**:
- 更强的推理和代码能力
- 同样支持 Function Calling
- 适合要求更高性能的场景

**适用场景**: 需要更强能力时使用


### 方案三：DeepSeek-Coder-V2-Lite-Instruct（16B）

**内存占用**: 约 20-30GB

**优势**:
- DeepSeek 最新代码模型
- 支持 Function Calling
- 内存占用小，适合资源受限场景
- 中英文代码能力强

**适用场景**: 资源节约型部署


### 方案四：Qwen2.5-14B-Instruct

**内存占用**: 约 18-25GB

**优势**:
- 通用能力强
- 支持 Function Calling
- 内存占用适中
- 中文支持优秀

**适用场景**: 平衡性能与资源


## 技术栈选择

### 推理引擎：vLLM（推荐）

- 高性能推理引擎
- 支持 OpenAI 兼容 API
- PagedAttention 优化内存使用
- 支持多用户并发

### 替代方案：Ollama

- 更简单易用
- 自动模型管理
- 兼容 OpenAI API（通过 litellm）


## 快速开始

### 方案一部署（Qwen2.5-Coder-32B + vLLM）

```bash
# 1. 克隆仓库
git clone https://github.com/githubstudycloud/gi009.git
cd gi009

# 2. 启动服务
docker-compose up -d

# 3. 等待模型加载（首次需要下载模型，约15-30分钟）
docker-compose logs -f

# 4. 测试服务
curl http://localhost:8000/v1/models
```

### 访问方式

- **API地址**: http://localhost:8000
- **兼容**: OpenAI API 格式
- **健康检查**: http://localhost:8000/health


## 与 Claude Code 集成

在 Claude Code 配置中添加：

```json
{
  "mcp_servers": {
    "local_llm": {
      "command": "node",
      "args": ["/path/to/openai-mcp-server"],
      "env": {
        "OPENAI_API_KEY": "dummy-key",
        "OPENAI_BASE_URL": "http://localhost:8000/v1"
      }
    }
  }
}
```


## 性能调优

### 并发用户配置

在 `docker-compose.yml` 中调整参数：

```yaml
--max-num-seqs 10        # 最大并发序列数（1-10用户）
--max-model-len 8192     # 上下文长度（根据需求调整）
--gpu-memory-utilization 0  # CPU模式
```

### 内存优化

- 使用量化模型（AWQ/GPTQ）可减少40-50%内存
- 调整 `--max-num-seqs` 控制并发
- 使用 `--swap-space` 启用内存交换


## 文件说明

- `docker-compose.yml`: Docker Compose 配置
- `docker-compose-ollama.yml`: Ollama 替代方案
- `docker-compose-deepseek.yml`: DeepSeek 模型配置
- `docker-compose-qwen72b.yml`: Qwen72B 大模型配置
- `test-api.sh`: API 测试脚本
- `benchmark.py`: 性能测试脚本


## 常见问题

### 1. 模型下载慢？

使用国内镜像站：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 2. 内存不足？

- 使用更小的模型（14B/16B）
- 减少 `--max-num-seqs`
- 启用模型量化

### 3. Function Calling 不生效？

确保模型支持工具调用，请求格式需包含 `tools` 参数：

```json
{
  "model": "qwen2.5-coder-32b-instruct",
  "messages": [...],
  "tools": [...]
}
```


## 维护与监控

### 查看日志
```bash
docker-compose logs -f
```

### 重启服务
```bash
docker-compose restart
```

### 停止服务
```bash
docker-compose down
```

### 更新模型
```bash
docker-compose pull
docker-compose up -d
```


## 参考资源

- [Qwen2.5 官方文档](https://qwen.readthedocs.io/)
- [vLLM 文档](https://docs.vllm.ai/)
- [OpenAI API 规范](https://platform.openai.com/docs/api-reference)


## 许可证

MIT License
