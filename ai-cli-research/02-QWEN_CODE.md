# Qwen Code CLI 详解

## 概述

Qwen Code 是阿里巴巴开源的 AI 编码代理工具，基于 Gemini CLI 分支开发，专为 Qwen3-Coder 模型优化。

- **开源协议**：Apache-2.0
- **默认模型**：Qwen3-Coder-480B-A35B
- **上下文窗口**：256K (原生) / 1M (扩展)
- **特点**：成本效益高，性能接近 Claude Sonnet 4

---

## 安装

### npm 安装 (推荐)

```bash
# 要求 Node.js >= 20
npm install -g @qwen-code/qwen-code@latest

# 验证安装
qwen --version
```

### Homebrew 安装 (macOS/Linux)

```bash
brew install qwen-code
```

### 源码安装

```bash
git clone https://github.com/QwenLM/qwen-code.git
cd qwen-code
npm install
npm install -g .
```

---

## 认证配置

### 方式 1：阿里云 API

```bash
export DASHSCOPE_API_KEY="your-api-key"
```

### 方式 2：OpenRouter

```bash
export OPENROUTER_API_KEY="your-key"
```

### 方式 3：HuggingFace

```bash
export HF_TOKEN="your-token"
```

### 方式 4：本地部署 (Ollama)

```bash
# 启动 Ollama
ollama serve

# 拉取模型
ollama pull qwen3-coder

# 配置 Qwen Code 使用本地模型
qwen --model ollama/qwen3-coder
```

---

## 配置文件

位置：`~/.qwen-code/settings.json`

```json
{
  "model": "qwen3-coder-480b",
  "apiKey": "${DASHSCOPE_API_KEY}",
  "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "coreTools": {
    "shell": { "requireConfirmation": false },
    "file_write": { "requireConfirmation": false }
  },
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    }
  }
}
```

---

## 核心功能

### 1. 深度代码理解

```bash
# 分析大型代码库
qwen "解释这个项目的架构"

# 跨文件重构
qwen "将所有 JavaScript 文件迁移到 TypeScript"
```

### 2. 工作流自动化

```bash
# PR 处理
qwen "审查并合并这个 PR"

# 格式化和 Lint
qwen "修复所有 ESLint 错误"

# 测试生成
qwen "为 src/utils 目录生成单元测试"
```

### 3. 多轮对话

```bash
# 启动交互模式
qwen

# 继续之前的会话
qwen --resume
```

---

## MCP 集成

### 配置 MCP 服务器

编辑 `~/.qwen-code/settings.json`：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

### 当前限制

> ⚠️ Qwen Code 目前不支持通过 CLI 参数传递 MCP 配置，需要在配置文件中设置。
>
> [相关 Issue #1278](https://github.com/QwenLM/qwen-code/issues/1278)

---

## 与 Claude Code 集成

### 方案 1：qwen-mcp-tool

让 Claude Code 调用 Qwen Code：

```bash
# 安装
git clone https://github.com/jeffery9/qwen-mcp-tool.git
cd qwen-mcp-tool
npm install && npm run build && npm link

# 添加到 Claude Code
claude mcp add qwen -- qwen-mcp-tool
```

### 方案 2：Qwen 作为后备模型

在 Claude Code 中配置 Qwen 作为成本较低的后备：

```json
// 使用自定义脚本桥接
{
  "mcpServers": {
    "qwen-fallback": {
      "command": "node",
      "args": ["./qwen-bridge.js"],
      "env": {
        "DASHSCOPE_API_KEY": "your-key"
      }
    }
  }
}
```

---

## 模型选择

| 模型 | 参数量 | 激活参数 | 适用场景 |
|------|--------|----------|----------|
| qwen3-coder-480b-a35b | 480B | 35B | 复杂编码任务 |
| qwen3-coder-32b | 32B | 32B | 通用编码 |
| qwen3-coder-7b | 7B | 7B | 本地部署、快速任务 |

```bash
# 使用不同模型
qwen --model qwen3-coder-32b "简单任务"
qwen --model qwen3-coder-480b-a35b "复杂重构"
```

---

## 常用命令

```bash
# 启动交互模式
qwen

# 单次任务
qwen "重构这个函数"

# 指定模型
qwen --model qwen3-coder-32b "任务"

# 指定工作目录
qwen --cwd /path/to/project

# 查看帮助
qwen --help
```

---

## 与其他工具对比

### vs Codex CLI

| 对比项 | Qwen Code | Codex CLI |
|--------|-----------|-----------|
| 成本 | 更低 | 较高 |
| 开源 | 是 | 是 |
| 中文支持 | **优秀** | 一般 |
| 本地部署 | 支持 | 不支持 |

### vs Gemini CLI

| 对比项 | Qwen Code | Gemini CLI |
|--------|-----------|------------|
| 代码库来源 | Fork 自 Gemini | 原版 |
| 模型优化 | Qwen 专属优化 | Gemini 原生 |
| 中国访问 | 友好 | 需 VPN |

---

## 优势与局限

### 优势

- **成本效益高**：性能接近顶级但价格更低
- **中文优化**：对中文代码注释和文档支持好
- **本地部署**：可使用 Ollama 本地运行
- **完全开源**：Apache-2.0 许可
- **中国访问友好**：无需翻墙

### 局限

- 复杂推理略逊于 Claude
- MCP CLI 配置支持不完善
- 社区生态相对较小
- 文档相对较少

---

## 参考资源

- [Qwen Code 官方文档](https://qwenlm.github.io/qwen-code-docs/en/)
- [Qwen Code GitHub](https://github.com/QwenLM/qwen-code)
- [Qwen3-Coder 发布博客](https://qwenlm.github.io/blog/qwen3-coder/)
- [Qwen-Agent 框架](https://github.com/QwenLM/Qwen-Agent)
