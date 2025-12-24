#!/bin/bash

# Claude API 格式测试脚本

API_URL="${API_URL:-http://localhost:8080}"
API_KEY="${API_KEY:-sk-1234567890abcdef}"

echo "========================================"
echo "Claude API 格式测试"
echo "API URL: $API_URL"
echo "========================================"
echo ""

# 1. 健康检查
echo "1. 测试健康检查..."
curl -s "$API_URL/health" | jq '.' || echo "健康检查失败"
echo ""

# 2. 列出可用模型
echo "2. 列出可用模型..."
curl -s "$API_URL/v1/models" \
  -H "x-api-key: $API_KEY" | jq '.' || echo "列出模型失败"
echo ""

# 3. 测试 Claude API 格式 - 基础对话
echo "3. 测试 Claude API 格式 - 基础对话..."
curl -s "$API_URL/v1/messages" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 200,
    "messages": [
      {"role": "user", "content": "你好，请用中文简单介绍一下你自己"}
    ]
  }' | jq '.content[0].text' || echo "Claude API 请求失败"
echo ""

# 4. 测试 Claude API 格式 - 代码生成
echo "4. 测试 Claude API 格式 - 代码生成..."
curl -s "$API_URL/v1/messages" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 500,
    "messages": [
      {"role": "user", "content": "用Python写一个快速排序函数"}
    ]
  }' | jq '.content[0].text' || echo "代码生成失败"
echo ""

# 5. 测试 Claude API 格式 - System Prompt
echo "5. 测试 System Prompt..."
curl -s "$API_URL/v1/messages" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 200,
    "system": "你是一个专业的编程助手，擅长Python和算法",
    "messages": [
      {"role": "user", "content": "二分查找的时间复杂度是多少？"}
    ]
  }' | jq '.content[0].text' || echo "System Prompt 测试失败"
echo ""

# 6. 测试流式响应
echo "6. 测试流式响应..."
curl -s "$API_URL/v1/messages" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 100,
    "stream": true,
    "messages": [
      {"role": "user", "content": "数到10"}
    ]
  }' | head -20 || echo "流式响应测试失败"
echo ""

# 7. 测试 OpenAI 格式兼容（可选）
echo "7. 测试 OpenAI 格式兼容..."
curl -s "$API_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "max_tokens": 50
  }' | jq '.choices[0].message.content' || echo "OpenAI 格式测试失败"
echo ""

# 8. 测试工具调用（如果模型支持）
echo "8. 测试工具调用（Claude API 格式）..."
curl -s "$API_URL/v1/messages" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 1024,
    "tools": [
      {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "input_schema": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "城市名称"
            }
          },
          "required": ["city"]
        }
      }
    ],
    "messages": [
      {"role": "user", "content": "北京今天天气怎么样？"}
    ]
  }' | jq '.' || echo "工具调用测试失败"
echo ""

echo "========================================"
echo "测试完成！"
echo ""
echo "如果看到错误，请检查："
echo "1. vLLM 服务是否正常运行"
echo "2. LiteLLM 代理是否启动"
echo "3. API_KEY 是否正确"
echo "4. 端口是否正确"
echo ""
echo "查看详细日志："
echo "  docker logs -f litellm-claude-proxy"
echo "  docker logs -f qwen-coder-vllm"
echo "========================================"
