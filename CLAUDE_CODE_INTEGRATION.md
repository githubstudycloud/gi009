# Claude Code 集成指南

本指南介绍如何将部署的本地大模型与 Claude Code 集成，实现工具调用功能。


## 方案概述

Claude Code 通过 MCP (Model Context Protocol) 服务器与 LLM 通信。我们可以使用 MCP 服务器桥接本地模型。

### 架构图

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │     MCP      │      │    vLLM      │
│ Claude Code  │ ───> │   Server     │ ───> │   API        │
│              │      │   (Bridge)   │      │  (本地模型)  │
└──────────────┘      └──────────────┘      └──────────────┘
```


## 方案一：使用 MCP OpenAI 桥接器

### 1. 安装 MCP OpenAI Server

```bash
npm install -g @modelcontextprotocol/server-openai
```

### 2. 配置 Claude Code

编辑 Claude Code 配置文件（通常在 `~/.config/claude-code/config.json`）：

```json
{
  "mcpServers": {
    "local-llm": {
      "command": "mcp-server-openai",
      "args": [],
      "env": {
        "OPENAI_API_KEY": "dummy-key",
        "OPENAI_BASE_URL": "http://localhost:8000/v1"
      }
    }
  }
}
```

### 3. 重启 Claude Code

```bash
claude-code restart
```


## 方案二：使用自定义 MCP 服务器

### 1. 创建 MCP 服务器项目

```bash
mkdir claude-code-local-bridge
cd claude-code-local-bridge
npm init -y
npm install @modelcontextprotocol/sdk openai
```

### 2. 创建服务器代码

创建 `index.js`:

```javascript
#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { OpenAI } from 'openai';

const LOCAL_API_URL = process.env.LOCAL_API_URL || 'http://localhost:8000/v1';
const MODEL_NAME = process.env.MODEL_NAME || 'qwen2.5-coder-32b-instruct';

// 创建 OpenAI 客户端
const client = new OpenAI({
  baseURL: LOCAL_API_URL,
  apiKey: 'dummy',
});

// 创建 MCP 服务器
const server = new Server(
  {
    name: 'local-llm-bridge',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 实现工具调用
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'chat',
        description: '与本地大模型对话',
        inputSchema: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: '用户消息',
            },
            system: {
              type: 'string',
              description: '系统提示词',
            },
          },
          required: ['message'],
        },
      },
      {
        name: 'code_generation',
        description: '生成代码',
        inputSchema: {
          type: 'object',
          properties: {
            task: {
              type: 'string',
              description: '代码生成任务描述',
            },
            language: {
              type: 'string',
              description: '编程语言',
            },
          },
          required: ['task'],
        },
      },
    ],
  };
});

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'chat') {
    const messages = [
      ...(args.system ? [{ role: 'system', content: args.system }] : []),
      { role: 'user', content: args.message },
    ];

    const response = await client.chat.completions.create({
      model: MODEL_NAME,
      messages,
      temperature: 0.7,
      max_tokens: 2000,
    });

    return {
      content: [
        {
          type: 'text',
          text: response.choices[0].message.content,
        },
      ],
    };
  }

  if (name === 'code_generation') {
    const messages = [
      {
        role: 'system',
        content: '你是一个专业的编程助手，擅长生成高质量的代码。',
      },
      {
        role: 'user',
        content: `请用${args.language || '合适的语言'}完成以下任务：${args.task}`,
      },
    ];

    const response = await client.chat.completions.create({
      model: MODEL_NAME,
      messages,
      temperature: 0.3,
      max_tokens: 3000,
    });

    return {
      content: [
        {
          type: 'text',
          text: response.choices[0].message.content,
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// 启动服务器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Local LLM MCP Server running on stdio');
}

main().catch(console.error);
```

### 3. 更新 package.json

```json
{
  "name": "claude-code-local-bridge",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "local-llm-bridge": "./index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "openai": "^4.0.0"
  }
}
```

### 4. 安装并配置

```bash
# 使桥接器全局可用
npm link

# 配置 Claude Code
```

在 Claude Code 配置中添加：

```json
{
  "mcpServers": {
    "local-llm": {
      "command": "local-llm-bridge",
      "env": {
        "LOCAL_API_URL": "http://localhost:8000/v1",
        "MODEL_NAME": "qwen2.5-coder-32b-instruct"
      }
    }
  }
}
```


## 方案三：使用 litellm 代理

### 1. 安装 litellm

```bash
pip install litellm
```

### 2. 创建配置文件

创建 `litellm_config.yaml`:

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/qwen2.5-coder-32b-instruct
      api_base: http://localhost:8000/v1
      api_key: dummy

general_settings:
  master_key: sk-1234
```

### 3. 启动 litellm 代理

```bash
litellm --config litellm_config.yaml --port 4000
```

### 4. 配置 Claude Code

```json
{
  "mcpServers": {
    "local-llm": {
      "command": "mcp-server-openai",
      "env": {
        "OPENAI_API_KEY": "sk-1234",
        "OPENAI_BASE_URL": "http://localhost:4000"
      }
    }
  }
}
```


## 使用示例

### 在 Claude Code 中使用

启动 Claude Code 后，你可以：

```bash
# 使用本地模型进行对话
> 你好，请介绍一下你自己

# 让模型生成代码
> 写一个 Python 快速排序函数

# 使用工具调用
> 帮我分析这段代码的时间复杂度
```


## 功能对比

| 功能 | 方案一 | 方案二 | 方案三 |
|------|--------|--------|--------|
| 安装难度 | 简单 | 中等 | 简单 |
| 自定义能力 | 低 | 高 | 中 |
| 性能 | 高 | 高 | 中 |
| 维护成本 | 低 | 中 | 低 |
| 推荐场景 | 快速测试 | 生产环境 | 多模型切换 |


## 高级配置

### 添加多个模型

```json
{
  "mcpServers": {
    "qwen-coder": {
      "command": "mcp-server-openai",
      "env": {
        "OPENAI_API_KEY": "dummy",
        "OPENAI_BASE_URL": "http://localhost:8000/v1",
        "OPENAI_MODEL": "qwen2.5-coder-32b-instruct"
      }
    },
    "deepseek": {
      "command": "mcp-server-openai",
      "env": {
        "OPENAI_API_KEY": "dummy",
        "OPENAI_BASE_URL": "http://localhost:8001/v1",
        "OPENAI_MODEL": "deepseek-coder-v2-lite"
      }
    }
  }
}
```

### 设置超时和重试

```json
{
  "mcpServers": {
    "local-llm": {
      "command": "mcp-server-openai",
      "env": {
        "OPENAI_API_KEY": "dummy",
        "OPENAI_BASE_URL": "http://localhost:8000/v1",
        "OPENAI_TIMEOUT": "300000",
        "OPENAI_MAX_RETRIES": "3"
      }
    }
  }
}
```


## 测试集成

### 1. 测试 MCP 服务器

```bash
# 列出可用工具
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | local-llm-bridge

# 调用工具
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "chat", "arguments": {"message": "Hello"}}}' | local-llm-bridge
```

### 2. 测试 Claude Code 集成

在 Claude Code 中运行：

```bash
claude-code doctor
```

检查 MCP 服务器状态。


## 故障排查

### 1. MCP 服务器无法启动

**检查项**：
- Node.js 版本 >= 18
- 依赖已正确安装
- 配置文件格式正确

**调试命令**：
```bash
# 查看 Claude Code 日志
claude-code logs

# 手动测试 MCP 服务器
local-llm-bridge
```

### 2. 无法连接本地 API

**检查项**：
- vLLM 服务正在运行
- 端口 8000 可访问
- 防火墙规则

**测试命令**：
```bash
curl http://localhost:8000/health
curl http://localhost:8000/v1/models
```

### 3. 工具调用失败

**可能原因**：
- 模型不支持 function calling
- 请求格式不正确
- 超时设置过短

**解决方案**：
- 确认使用支持工具调用的模型（Qwen2.5、DeepSeek-V2）
- 增加超时时间
- 查看详细错误日志


## 性能优化

### 1. 启用缓存

在 MCP 服务器中添加响应缓存：

```javascript
import { LRUCache } from 'lru-cache';

const cache = new LRUCache({
  max: 100,
  ttl: 1000 * 60 * 60, // 1 hour
});

// 在调用前检查缓存
const cacheKey = JSON.stringify(messages);
const cached = cache.get(cacheKey);
if (cached) {
  return cached;
}

// 调用后保存缓存
const result = await client.chat.completions.create(...);
cache.set(cacheKey, result);
```

### 2. 并发请求限制

```javascript
import pLimit from 'p-limit';

const limit = pLimit(5); // 最多5个并发请求

// 在工具调用中使用
await limit(() => client.chat.completions.create(...));
```

### 3. 流式响应

对于长响应，使用流式传输：

```javascript
const stream = await client.chat.completions.create({
  model: MODEL_NAME,
  messages,
  stream: true,
});

let fullResponse = '';
for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content || '';
  fullResponse += content;
  // 可以实时发送给 Claude Code
}
```


## 安全建议

1. **不要在配置中硬编码敏感信息**
2. **使用环境变量存储 API 密钥**
3. **限制 MCP 服务器的网络访问**
4. **启用请求日志审计**
5. **定期更新依赖包**


## 示例项目

完整的示例项目可在以下位置找到：

```bash
git clone https://github.com/githubstudycloud/gi009.git
cd gi009/examples/claude-code-integration
npm install
npm start
```


## 进阶话题

### 自定义工具

你可以为本地模型添加自定义工具：

```javascript
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      // ... 其他工具
      {
        name: 'execute_python',
        description: '执行 Python 代码',
        inputSchema: {
          type: 'object',
          properties: {
            code: { type: 'string', description: 'Python 代码' },
          },
          required: ['code'],
        },
      },
    ],
  };
});

server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'execute_python') {
    // 实现 Python 代码执行逻辑
    const result = await executePython(request.params.arguments.code);
    return { content: [{ type: 'text', text: result }] };
  }
});
```

### 多模型路由

根据任务类型选择不同的模型：

```javascript
function selectModel(task) {
  if (task.includes('代码') || task.includes('code')) {
    return 'qwen2.5-coder-32b-instruct';
  } else if (task.includes('数学') || task.includes('math')) {
    return 'qwen2.5-72b-instruct';
  } else {
    return 'qwen2.5-coder-32b-instruct'; // 默认
  }
}
```


## 相关资源

- [MCP 协议文档](https://modelcontextprotocol.io/)
- [Claude Code 文档](https://docs.anthropic.com/claude/docs/claude-code)
- [OpenAI API 规范](https://platform.openai.com/docs/api-reference)
- [vLLM 文档](https://docs.vllm.ai/)


## 常见问题

### Q: 本地模型能完全替代 Claude 吗？

A: 不能完全替代，但可以作为补充：
- 本地模型适合代码生成、文档编写等任务
- Claude 在复杂推理、创意写作方面更强
- 建议结合使用，发挥各自优势

### Q: 响应速度会比 Claude API 慢吗？

A: 取决于硬件配置：
- CPU 推理：比 Claude API 慢 3-10 倍
- GPU 推理：接近或超过 Claude API
- 本地部署的优势是没有网络延迟和 API 限制

### Q: 如何监控使用情况？

A: 可以添加日志和监控：
```javascript
// 在 MCP 服务器中添加
let requestCount = 0;
server.setRequestHandler('tools/call', async (request) => {
  requestCount++;
  console.log(`Request #${requestCount}: ${request.params.name}`);
  // ...
});
```


## 下一步

- 尝试 [API 使用示例](./API.md)
- 查看 [部署指南](./DEPLOYMENT.md)
- 探索 [性能优化技巧](./OPTIMIZATION.md)
