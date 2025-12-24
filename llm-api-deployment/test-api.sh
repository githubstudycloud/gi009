#!/bin/bash

# API测试脚本

API_URL="${API_URL:-http://localhost:8000}"
MODEL_NAME="${MODEL_NAME:-qwen2.5-coder-32b-instruct}"

echo "========================================"
echo "API 测试脚本"
echo "API URL: $API_URL"
echo "========================================"
echo ""

# 1. 健康检查
echo "1. 测试健康检查..."
curl -s "$API_URL/health" | jq '.'
echo ""

# 2. 列出可用模型
echo "2. 列出可用模型..."
curl -s "$API_URL/v1/models" | jq '.'
echo ""

# 3. 测试基础对话
echo "3. 测试基础对话..."
curl -s "$API_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$MODEL_NAME"'",
    "messages": [
      {"role": "user", "content": "你好，请用中文自我介绍一下"}
    ],
    "temperature": 0.7,
    "max_tokens": 200
  }' | jq '.choices[0].message.content'
echo ""

# 4. 测试代码生成
echo "4. 测试代码生成..."
curl -s "$API_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$MODEL_NAME"'",
    "messages": [
      {"role": "user", "content": "用Python写一个快速排序函数"}
    ],
    "temperature": 0.3,
    "max_tokens": 500
  }' | jq '.choices[0].message.content'
echo ""

# 5. 测试 Function Calling
echo "5. 测试 Function Calling..."
curl -s "$API_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$MODEL_NAME"'",
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
                "description": "城市名称，例如：北京、上海"
              },
              "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "温度单位"
              }
            },
            "required": ["city"]
          }
        }
      }
    ],
    "tool_choice": "auto"
  }' | jq '.'
echo ""

echo "========================================"
echo "测试完成！"
echo "========================================"
