# API 使用指南

本项目提供完全兼容 OpenAI API 格式的接口，可以无缝替换 OpenAI API。


## API 端点

### 基础 URL

```
http://localhost:8000
```

### 可用端点

- `GET /health` - 健康检查
- `GET /v1/models` - 列出可用模型
- `POST /v1/chat/completions` - 对话补全（支持流式和非流式）
- `POST /v1/completions` - 文本补全


## 认证

默认配置无需认证。如需启用认证，可以使用 API Key：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  ...
```


## 基础使用

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

响应：
```json
{
  "status": "ok"
}
```

### 2. 列出模型

```bash
curl http://localhost:8000/v1/models
```

响应：
```json
{
  "object": "list",
  "data": [
    {
      "id": "qwen2.5-coder-32b-instruct",
      "object": "model",
      "created": 1234567890,
      "owned_by": "vllm"
    }
  ]
}
```

### 3. 基础对话

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [
      {"role": "system", "content": "你是一个专业的编程助手"},
      {"role": "user", "content": "用Python写一个快速排序"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### 4. 流式响应

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [
      {"role": "user", "content": "解释什么是Docker"}
    ],
    "stream": true
  }'
```


## Function Calling（工具调用）

### 基础示例

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [
      {"role": "user", "content": "北京今天天气怎么样？"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "获取指定城市的天气信息",
          "parameters": {
            "type": "object",
            "properties": {
              "city": {
                "type": "string",
                "description": "城市名称"
              },
              "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"]
              }
            },
            "required": ["city"]
          }
        }
      }
    ],
    "tool_choice": "auto"
  }'
```

响应示例：
```json
{
  "id": "cmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "qwen2.5-coder-32b-instruct",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_xxx",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"city\": \"北京\", \"unit\": \"celsius\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

### 多轮对话与工具调用

```python
import requests
import json

API_URL = "http://localhost:8000/v1/chat/completions"
MODEL = "qwen2.5-coder-32b-instruct"

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "搜索代码仓库",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "language": {"type": "string", "description": "编程语言"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"]
            }
        }
    }
]

# 第一轮：用户请求
messages = [
    {"role": "user", "content": "帮我找到快速排序的Python实现"}
]

response = requests.post(
    API_URL,
    json={
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto"
    }
).json()

assistant_message = response["choices"][0]["message"]
messages.append(assistant_message)

# 如果模型调用了工具
if assistant_message.get("tool_calls"):
    for tool_call in assistant_message["tool_calls"]:
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        # 执行工具（这里模拟）
        if function_name == "search_code":
            result = "找到文件：algorithms/sorting.py"
        elif function_name == "read_file":
            result = "def quicksort(arr): ..."

        # 添加工具结果到消息
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": result
        })

    # 第二轮：获取最终响应
    response = requests.post(
        API_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "tools": tools
        }
    ).json()

    print(response["choices"][0]["message"]["content"])
```


## 参数说明

### 常用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | string | 必需 | 模型名称 |
| `messages` | array | 必需 | 对话消息列表 |
| `temperature` | float | 0.7 | 采样温度 (0-2) |
| `top_p` | float | 1.0 | 核采样 (0-1) |
| `max_tokens` | integer | 无限制 | 最大生成token数 |
| `stream` | boolean | false | 是否流式返回 |
| `tools` | array | null | 可用工具列表 |
| `tool_choice` | string/object | "auto" | 工具选择策略 |

### Temperature 参数

- `0.0-0.3`: 更确定性，适合代码生成、事实性回答
- `0.4-0.7`: 平衡创造性和确定性（推荐）
- `0.8-1.0`: 更有创造性，适合创意写作
- `1.0+`: 高度随机，一般不推荐

### Top-p 参数

- `0.1`: 非常保守
- `0.5`: 中等多样性
- `0.9`: 高多样性（推荐）
- `1.0`: 最大多样性

### Tool Choice 参数

- `"auto"`: 自动决定是否调用工具（推荐）
- `"none"`: 不调用任何工具
- `{"type": "function", "function": {"name": "function_name"}}`: 强制调用指定工具


## Python SDK 示例

### 使用 OpenAI SDK

```python
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # vLLM 不需要真实的 API key
)

# 基础对话
response = client.chat.completions.create(
    model="qwen2.5-coder-32b-instruct",
    messages=[
        {"role": "system", "content": "你是一个专业的编程助手"},
        {"role": "user", "content": "写一个Python快速排序"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)

# 流式响应
stream = client.chat.completions.create(
    model="qwen2.5-coder-32b-instruct",
    messages=[{"role": "user", "content": "解释Docker的原理"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 使用 Function Calling

```python
from openai import OpenAI
import json

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "执行Python代码并返回结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的Python代码"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

# 发送请求
response = client.chat.completions.create(
    model="qwen2.5-coder-32b-instruct",
    messages=[
        {"role": "user", "content": "计算1到100的和"}
    ],
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message

# 处理工具调用
if message.tool_calls:
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print(f"调用工具: {function_name}")
        print(f"参数: {arguments}")

        # 执行工具（这里模拟）
        if function_name == "execute_code":
            result = eval(arguments["code"])
            print(f"结果: {result}")
```


## JavaScript/TypeScript 示例

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'dummy',
});

// 基础对话
async function chat() {
  const response = await client.chat.completions.create({
    model: 'qwen2.5-coder-32b-instruct',
    messages: [
      { role: 'user', content: '写一个TypeScript接口定义用户信息' }
    ],
    temperature: 0.7,
    max_tokens: 500,
  });

  console.log(response.choices[0].message.content);
}

// 流式响应
async function streamChat() {
  const stream = await client.chat.completions.create({
    model: 'qwen2.5-coder-32b-instruct',
    messages: [
      { role: 'user', content: '解释React Hooks' }
    ],
    stream: true,
  });

  for await (const chunk of stream) {
    process.stdout.write(chunk.choices[0]?.delta?.content || '');
  }
}

// Function Calling
async function functionCall() {
  const tools = [
    {
      type: 'function',
      function: {
        name: 'get_user_info',
        description: '获取用户信息',
        parameters: {
          type: 'object',
          properties: {
            user_id: { type: 'string' }
          },
          required: ['user_id']
        }
      }
    }
  ];

  const response = await client.chat.completions.create({
    model: 'qwen2.5-coder-32b-instruct',
    messages: [
      { role: 'user', content: '获取用户123的信息' }
    ],
    tools: tools,
    tool_choice: 'auto',
  });

  const message = response.choices[0].message;

  if (message.tool_calls) {
    for (const toolCall of message.tool_calls) {
      console.log('调用工具:', toolCall.function.name);
      console.log('参数:', JSON.parse(toolCall.function.arguments));
    }
  }
}
```


## curl 示例集合

### 代码生成

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [
      {
        "role": "user",
        "content": "用Python实现一个LRU缓存，要求：\n1. 支持get和put操作\n2. O(1)时间复杂度\n3. 包含完整的类型注解"
      }
    ],
    "temperature": 0.3,
    "max_tokens": 2000
  }'
```

### 代码审查

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [
      {
        "role": "user",
        "content": "请审查以下代码并指出问题：\n```python\ndef divide(a, b):\n    return a / b\n```"
      }
    ],
    "temperature": 0.5
  }'
```

### 文档生成

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder-32b-instruct",
    "messages": [
      {
        "role": "user",
        "content": "为以下函数生成详细的docstring：\n```python\ndef merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n```"
      }
    ]
  }'
```


## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 400 | 请求参数错误 | 检查请求格式和参数 |
| 500 | 服务器内部错误 | 查看服务日志 |
| 503 | 服务不可用 | 检查服务是否正常运行 |

### 错误响应示例

```json
{
  "error": {
    "message": "Invalid request parameters",
    "type": "invalid_request_error",
    "code": 400
  }
}
```


## 性能优化建议

1. **批处理请求**：对于多个独立请求，使用并发而不是串行
2. **合理设置 max_tokens**：避免生成过长的响应
3. **使用流式响应**：改善用户体验
4. **缓存常见请求**：减少重复计算
5. **监控响应时间**：及时发现性能问题


## 下一步

- 查看 [Claude Code 集成指南](./CLAUDE_CODE_INTEGRATION.md)
- 运行 [性能测试](./benchmark.py)
- 阅读 [部署指南](./DEPLOYMENT.md)
