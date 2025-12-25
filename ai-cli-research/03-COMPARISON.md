# AI CLI 工具全面对比

## 工具概览

| 工具 | 厂商 | 首发 | 开源 | 许可证 |
|------|------|------|------|--------|
| Claude Code | Anthropic | 2024 | 否 | 专有 |
| Codex CLI | OpenAI | 2025 | 是 | Apache-2.0 |
| Gemini CLI | Google | 2025 | 是 | Apache-2.0 |
| Qwen Code | Alibaba | 2025.07 | 是 | Apache-2.0 |

---

## 安装方式对比

```bash
# Claude Code
npm install -g @anthropic-ai/claude-code

# Codex CLI
npm install -g @openai/codex
# 或
brew install --cask codex

# Gemini CLI
npm install -g @anthropic-ai/gemini-cli

# Qwen Code
npm install -g @qwen-code/qwen-code
# 或
brew install qwen-code
```

---

## 模型与性能

| 工具 | 默认模型 | 上下文窗口 | Terminal Bench 排名 |
|------|----------|------------|---------------------|
| Claude Code | Claude 4 Opus/Sonnet | 200K | #3 |
| Codex CLI | GPT-5.2-Codex | 标准 | #19 |
| Gemini CLI | Gemini 2.5 Pro | **1M** | 中等 |
| Qwen Code | Qwen3-Coder-480B | 256K-1M | 接近 Claude |

---

## 定价对比

| 工具 | 免费额度 | 付费起价 |
|------|----------|----------|
| Claude Code | 无 | $20/月 (Pro) |
| Codex CLI | API 付费 | 按量计费 |
| Gemini CLI | **60次/分, 1000次/天** | Vertex AI 计费 |
| Qwen Code | 阿里云免费额度 | 按量计费 (最便宜) |

---

## 功能对比矩阵

| 功能 | Claude Code | Codex CLI | Gemini CLI | Qwen Code |
|------|:-----------:|:---------:|:----------:|:---------:|
| **MCP 原生支持** | ✅ | ✅ | ✅ | ✅ |
| **Docker 沙箱** | ✅ | ✅ | ✅ (默认) | ✅ |
| **多模态输入** | ✅ | ✅ | ✅✅ | ✅ |
| **斜杠命令** | ✅ | ✅ | ✅ | ✅ |
| **自定义技能** | ✅ | ✅ | ✅ | ⚠️ |
| **GitHub 集成** | ✅ | ✅✅ | ✅ | ✅ |
| **本地模型** | ❌ | ❌ | ❌ | ✅ |
| **中文优化** | ⚠️ | ⚠️ | ⚠️ | ✅✅ |
| **Windows 原生** | ✅ | ⚠️ (WSL) | ⚠️ | ⚠️ |

---

## MCP 集成对比

### Claude Code

```json
// ~/.claude/config.json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "mcp-server"]
    }
  }
}
```

```bash
# CLI 添加
claude mcp add name -- command args
```

### Codex CLI

```toml
# ~/.codex/config.toml
[mcp_servers.server-name]
type = "stdio"
command = "npx"
args = ["-y", "mcp-server"]
```

```bash
# CLI 添加
codex mcp add name -- command args
```

### Gemini CLI

```json
// ~/.gemini/settings.json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "mcp-server"]
    }
  }
}
```

```bash
# CLI 添加
gemini mcp add name -- command args
```

### Qwen Code

```json
// ~/.qwen-code/settings.json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "mcp-server"]
    }
  }
}
```

> ⚠️ Qwen Code 目前不支持 CLI 方式添加 MCP 服务器

---

## 作为 MCP 服务器运行

| 工具 | 命令 | 暴露工具 |
|------|------|----------|
| Claude Code | `claude-code mcp-server` | 多种 |
| Codex CLI | `codex mcp-server` | `codex()`, `codex-reply()` |
| Gemini CLI | `gemini mcp-server` | 多种 |
| Qwen Code | 需第三方封装 | - |

---

## 适用场景推荐

### Claude Code 最适合

- 复杂工程项目和深度推理
- 需要高可靠性的生产环境
- 多文件重构和架构设计
- 团队协作工作流

### Codex CLI 最适合

- 快速原型和实验
- CI/CD 集成和 GitHub Actions
- 脚本自动化任务
- 熟悉 OpenAI 生态的团队

### Gemini CLI 最适合

- 大型代码库分析 (1M 上下文)
- 多模态工作流 (图片/视频/PDF)
- Google Cloud 深度集成
- 预算敏感项目 (免费额度)

### Qwen Code 最适合

- 中文项目和文档
- 成本敏感场景
- 本地部署需求
- 中国大陆访问

---

## 跨工具协作方案

### Claude Code 作为主控

```
┌─────────────┐
│ Claude Code │ (策略规划、复杂推理)
└──────┬──────┘
       │ MCP
       ├──────────┬──────────┬──────────┐
       ▼          ▼          ▼          ▼
   ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
   │ Codex │  │Gemini │  │ Qwen  │  │ 其他  │
   │  MCP  │  │  MCP  │  │  MCP  │  │  MCP  │
   └───────┘  └───────┘  └───────┘  └───────┘
```

### 配置示例

```json
// Claude Code 配置
{
  "mcpServers": {
    "codex": {
      "command": "npx",
      "args": ["-y", "codex-mcp-server"]
    },
    "gemini": {
      "command": "gemini",
      "args": ["mcp-server"]
    },
    "qwen": {
      "command": "qwen-mcp-tool"
    }
  }
}
```

---

## 基准测试参考

### Terminal Bench (2025)

| 排名 | 工具 | 得分 |
|------|------|------|
| #1 | Claude 4 Opus | 92.3 |
| #3 | Claude Code | 89.1 |
| #5 | Qwen3-Coder-480B | 87.2 |
| #8 | Gemini 2.5 Pro | 84.5 |
| #19 | Codex CLI | 71.8 |

### 实际任务测试

| 任务类型 | 最佳工具 |
|----------|----------|
| C → Go 转换 | Codex CLI |
| 前端开发 | Claude Code |
| 大代码库分析 | Gemini CLI |
| 中文文档生成 | Qwen Code |

---

## 选择建议

```
如果你需要...
├── 最高可靠性 → Claude Code
├── 最大上下文 → Gemini CLI
├── 最低成本 → Qwen Code
├── 最快迭代 → Codex CLI
├── 本地部署 → Qwen Code
├── 中文支持 → Qwen Code
└── 多模态输入 → Gemini CLI
```

---

## 参考资源

- [CLI 工具对比 - CodeAnt](https://www.codeant.ai/blogs/claude-code-cli-vs-codex-cli-vs-gemini-cli-best-ai-cli-tool-for-developers-in-2025)
- [AI CLI 选择指南 - AI Native Dev](https://ainativedev.io/news/choosing-the-right-ai-cli)
- [三大 CLI 对比 - Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/08/codex-cli-vs-gemini-cli-vs-claude-code/)
