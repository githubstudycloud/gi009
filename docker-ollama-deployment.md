# Docker部署支持工具调用的大模型方案

## 一、方案概述

针对您的需求（Ubuntu 18.04.2，E5-2680 CPU，363GB内存，1-10人使用），推荐使用**Ollama**框架部署开源大模型，该方案具有以下优势：

- ✅ 开源免费，支持多平台
- ✅ 内存运行（CPU模式），无需GPU
- ✅ 支持工具调用功能
- ✅ 中文支持良好
- ✅ 模型丰富，更新及时
- ✅ Docker部署，配置简单
- ✅ 支持API调用，方便集成

## 二、模型选择

根据您的内存需求（50-100GB），推荐以下模型：

| 模型名称 | 内存需求 | 特点 |
|---------|---------|------|
| **Qwen2.5-14B-Instruct** | ~30-40GB | 阿里云开源，中文支持优秀，代码能力强 |
| **DeepSeek-R1-32B-Chat** | ~60-80GB | 深度求索最新模型，性能接近闭源模型，支持工具调用 |
| **Qwen2.5-32B-Instruct** | ~60-80GB | 更大参数规模，更强的理解和生成能力 |
| **DeepSeek-V3-16B-Chat** | ~35-45GB | 支持工具调用，代码生成能力强 |

**推荐首选**：DeepSeek-R1-32B-Chat（约70GB内存），该模型在开源模型中性能排名靠前，支持工具调用，中文处理能力优秀。

## 三、部署步骤

### 1. 环境准备

#### 1.1 安装Docker
```bash
# 更新软件包
sudo apt-get update

# 安装依赖
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common

# 添加Docker GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# 添加Docker仓库
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"

# 安装Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

#### 1.2 安装Docker Compose
```bash
# 下载Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 2. 部署Ollama服务

#### 2.1 创建Docker Compose配置文件

创建`docker-compose.yml`文件：
```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    volumes:
      - ./ollama:/root/.ollama
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_MAX_LOADED_MODELS=3
      - OLLAMA_NUM_PARALLEL=10
    deploy:
      resources:
        limits:
          memory: 100G
        reservations:
          memory: 80G

  # 可选：部署Web界面
  open-webui:
    image: ghcr.io/open-webui/open-webui:latest
    container_name: open-webui
    restart: unless-stopped
    ports:
      - "3000:8080"
    volumes:
      - ./open-webui:/app/backend/data
    depends_on:
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
```

#### 2.2 启动服务

```bash
# 创建数据目录
mkdir -p ollama open-webui

# 启动服务
docker-compose up -d
```

### 3. 拉取和运行模型

#### 3.1 进入Ollama容器

```bash
docker exec -it ollama bash
```

#### 3.2 拉取模型

根据您的内存选择合适的模型：

```bash
# 拉取Qwen2.5-14B-Instruct（约35GB内存）
ollama pull qwen2.5:14b-instruct

# 或拉取DeepSeek-R1-32B-Chat（约70GB内存）
ollama pull deepseek-r1:32b-chat

# 或拉取Qwen2.5-32B-Instruct（约65GB内存）
ollama pull qwen2.5:32b-instruct
```

#### 3.3 查看已加载的模型

```bash
ollama list
```

### 4. 配置工具调用

#### 4.1 创建工具定义文件

在宿主机上创建`tools.json`文件：

```json
[
  {
    "type": "function",
    "function": {
      "name": "code_interpreter",
      "description": "执行Python代码并返回结果，用于数据分析、计算和代码验证",
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
  },
  {
    "type": "function",
    "function": {
      "name": "web_search",
      "description": "搜索网络获取最新信息",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "搜索关键词"
          }
        },
        "required": ["query"]
      }
    }
  }
]
```

#### 4.2 配置模型支持工具调用

创建模型配置文件（例如`deepseek-r1-tools.Modelfile`）：

```bash
FROM deepseek-r1:32b-chat

# 启用工具调用
PARAMETER toolcall true

# 配置工具列表
TOOLDEFINITIONS "$(cat /root/.ollama/tools.json)"

# 设置上下文窗口大小
PARAMETER num_ctx 8192

# 设置生成参数
PARAMETER temperature 0.7
PARAMETER top_p 0.9
```

#### 4.3 创建自定义模型

```bash
# 将tools.json复制到容器内
docker cp tools.json ollama:/root/.ollama/

docker exec -it ollama bash

# 创建自定义模型
ollama create deepseek-r1-tools -f /root/.ollama/deepseek-r1-tools.Modelfile
```

## 四、使用方法

### 1. 通过Web界面使用

访问 `http://您的服务器IP:3000`，即可使用Open WebUI与模型交互。

### 2. 通过API调用

#### 2.1 基本聊天API

```bash
curl http://localhost:11434/api/chat -d '{  
  "model": "deepseek-r1-tools",
  "messages": [
    {"role": "user", "content": "写一个Python脚本，计算斐波那契数列的前20项"}
  ],
  "stream": true
}'
```

#### 2.2 工具调用示例

```bash
curl http://localhost:11434/api/chat -d '{  
  "model": "deepseek-r1-tools",
  "messages": [
    {"role": "user", "content": "计算2023年中国GDP增长率，并生成一个简单的图表"}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "code_interpreter",
        "description": "执行Python代码",
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
  ],
  "stream": true
}'
```

## 五、性能优化建议

1. **调整内存分配**：根据实际使用情况调整Docker Compose中的内存限制
2. **优化模型参数**：
   - 对于代码生成，可降低`temperature`至0.3-0.5
   - 对于创意写作，可提高`temperature`至0.7-0.9
3. **增加上下文窗口**：根据需要调整`num_ctx`参数（建议8192-16384）
4. **调整并行数**：根据用户数量调整`OLLAMA_NUM_PARALLEL`参数
5. **预加载模型**：将常用模型预加载到内存中

## 六、监控和维护

### 1. 查看日志

```bash
# 查看Ollama日志
docker logs -f ollama

# 查看WebUI日志
docker logs -f open-webui
```

### 2. 更新模型

```bash
docker exec -it ollama bash
ollama pull deepseek-r1:32b-chat
ollama create deepseek-r1-tools -f /root/.ollama/deepseek-r1-tools.Modelfile
```

### 3. 监控资源使用

```bash
docker stats
```

## 七、常见问题解决

1. **内存不足错误**：
   - 降低模型参数规模
   - 调整Docker内存限制
   - 关闭不必要的其他服务

2. **模型加载缓慢**：
   - 确保使用SSD存储
   - 预加载常用模型
   - 调整`OLLAMA_MAX_LOADED_MODELS`参数

3. **工具调用失败**：
   - 检查工具定义是否正确
   - 确保模型支持工具调用
   - 查看Ollama日志排查问题

## 八、总结

本方案基于Ollama框架，结合DeepSeek或Qwen模型，能够满足您的需求：

- ✅ 支持工具调用，可用于代码生成、数据分析等场景
- ✅ 中文支持良好，适合中文文档和代码编写
- ✅ 内存使用在50-100GB范围内，适合您的服务器配置
- ✅ 支持1-10人同时使用
- ✅ Docker部署，配置简单，易于维护
- ✅ 开源免费，可根据需要扩展功能

您可以根据实际使用情况调整模型和参数，以获得最佳的性能和用户体验。