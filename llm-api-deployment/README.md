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

## 🆕 2025年最新推荐模型

### 方案一：Qwen3-Coder-30B-A3B（2025最新推荐）🔥

**内存占用**: 约 25-35GB

**优势**:
- 🚀 2024年12月最新发布，MoE架构
- ⚡ 仅3.3B激活参数，内存占用低
- 🧠 混合推理模式（thinking + non-thinking）
- 💪 超越QwQ-32B，10倍激活参数的性能
- 🎯 128个专家，32K-131K上下文
- 🛠️ 原生支持 Function Calling

**部署命令**:
```bash
docker-compose -f docker-compose-qwen3.yml up -d
```

**适用场景**: 复杂代码推理、资源受限高性能需求、混合推理任务


### 方案二：GLM-4.5-Air（工具调用专家）🔥

**内存占用**: 约 35-50GB

**优势**:
- 🤖 专为Agent和工具调用优化
- 📜 MIT开源，可商用
- 🔧 原生工具调用（web浏览、代码执行、API集成）
- 🧠 106B参数，12B激活（MoE）
- 📊 128K上下文
- 🇨🇳 中文支持优秀

**部署命令**:
```bash
docker-compose -f docker-compose-glm45air.yml up -d
```

**适用场景**: Agent开发、复杂工具调用、企业商用


### 方案三：DeepSeek-V3（顶级性能）🔥

**内存占用**: 约 60-80GB

**优势**:
- 🏆 开源模型最强，接近GPT-4
- 💎 671B参数，37B激活（MoE）
- 🎓 强大推理和代码能力
- 📚 14.8T tokens预训练
- 🔥 通用前沿助手

**部署命令**:
```bash
docker-compose -f docker-compose-deepseek-v3.yml up -d
```

**适用场景**: 追求最佳性能、充足内存环境


## 经典稳定方案

### 方案四：Qwen2.5-Coder-32B-Instruct（成熟稳定）⭐

**内存占用**: 约 40-50GB

**优势**:
- 成熟稳定，文档完善
- 原生支持 Function Calling
- 中文和代码能力强
- 32B参数，128K上下文
- 生态完善

**部署命令**:
```bash
docker-compose up -d
```

**适用场景**: 生产环境、稳定性要求高


### 方案五：DeepSeek-Coder-V2-Lite（资源节约）

**内存占用**: 约 20-30GB

**优势**:
- 内存占用小
- 推理速度快
- 代码能力强（16B参数）
- 支持 Function Calling

**部署命令**:
```bash
docker-compose -f docker-compose-deepseek.yml up -d
```

**适用场景**: 资源受限环境


### 方案六：QwQ-32B（深度推理）

**内存占用**: 约 40-50GB

**优势**:
- 🧠 专注深度推理任务
- 📊 32.5B参数，32K-131K上下文
- 🎯 Apache 2.0开源
- 💡 特别适合复杂逻辑问题

**劣势**:
- ⚠️ Function Calling支持有限
- ⚠️ 更适合推理而非工具调用

**部署命令**:
```bash
docker-compose -f docker-compose-qwq32b.yml up -d
```

**适用场景**: 数学问题、逻辑推理、复杂思考任务


### 方案七：Gemma 3 27B（Google新品）

**内存占用**: 约 35-45GB

**优势**:
- 🌟 Google 2025年新发布
- 🔧 原生Function Calling（Gemma 3特性）
- 📚 128K上下文
- 🚀 单GPU即可运行
- 🎓 13T tokens训练

**部署命令**:
```bash
docker-compose -f docker-compose-gemma3.yml up -d
```

**适用场景**: Google生态集成、函数调用、多轮对话


## 快速选择指南

| 需求 | 推荐模型 | CPU内存 | GPU显存(INT4) | 特点 |
|------|---------|---------|--------------|------|
| 最新代码生成 | Qwen3-Coder-30B-A3B 🔥 | 25-35GB | 15-20GB | MoE，混合推理 |
| Agent/工具调用 | GLM-4.5-Air 🔥 | 35-50GB | 20-25GB | 工具专家，MIT开源 |
| 顶级性能 | DeepSeek-V3 🔥 | 60-80GB | 35-40GB | 接近GPT-4 |
| 深度推理 | QwQ-32B | 40-50GB | 20-24GB | 数学逻辑专家 |
| Google生态 | Gemma 3 27B | 35-45GB | 16-20GB | 原生工具调用 |
| 生产稳定 | Qwen2.5-Coder-32B | 40-50GB | 20-24GB | 成熟方案 |
| 资源受限 | DeepSeek-V2-Lite | 20-30GB | 10-12GB | 快速高效 |

详细对比：[MODEL_COMPARISON.md](./MODEL_COMPARISON.md)

**硬件需求详解**: [HARDWARE_REQUIREMENTS.md](./HARDWARE_REQUIREMENTS.md) 📊

### 💾 CPU vs GPU 内存对比

**CPU 内存推理**（本项目主要方案）:
- ✅ 无需GPU，使用系统内存
- ✅ 内存容量大（64GB-512GB常见）
- ✅ 部署简单，成本低
- ⚠️ 速度较慢（5-15 tokens/秒）

**GPU 显存推理**:
- ✅ 速度快（50-100+ tokens/秒）
- ✅ 延迟低（<1秒首token）
- ⚠️ 需要高端GPU（RTX 4090/A100）
- ⚠️ 显存有限（24GB-80GB）

**详细硬件需求和性能对比**: 查看 [HARDWARE_REQUIREMENTS.md](./HARDWARE_REQUIREMENTS.md)


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
