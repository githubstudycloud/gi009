# AI CLI 工具研究

本目录包含主流 AI CLI 工具的研究文档，对比分析各工具的功能、配置和集成方案。

## 研究对象

| 工具 | 开发商 | 开源 | 主要模型 |
|------|--------|------|----------|
| Claude Code | Anthropic | 否 | Claude 4 Opus/Sonnet |
| Codex CLI | OpenAI | 是 (Apache-2.0) | GPT-5.2-Codex |
| Gemini CLI | Google | 是 (Apache-2.0) | Gemini 2.5 Pro |
| Qwen Code | Alibaba | 是 (Apache-2.0) | Qwen3-Coder |

## 文档目录

```
ai-cli-research/
├── README.md                    # 本文件
├── 01-GEMINI_CLI.md            # Gemini CLI 详解
├── 02-QWEN_CODE.md             # Qwen Code 详解
├── 03-COMPARISON.md            # 四大 CLI 工具对比
└── 04-INTEGRATION.md           # 跨工具集成方案
```

## 快速对比

| 特性 | Claude Code | Codex CLI | Gemini CLI | Qwen Code |
|------|-------------|-----------|------------|-----------|
| 免费额度 | 无 | API 付费 | 60次/分钟 | API 付费 |
| 上下文窗口 | 200K | 标准 | **1M** | 256K-1M |
| MCP 支持 | 原生 | 原生 | 原生 | 原生 |
| Docker 沙箱 | 支持 | 支持 | **默认** | 支持 |
| 多模态 | 支持 | 支持 | **最强** | 支持 |

## 参考资源

- [Claude Code 官网](https://claude.ai/code)
- [Codex CLI GitHub](https://github.com/openai/codex)
- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Qwen Code GitHub](https://github.com/QwenLM/qwen-code)
