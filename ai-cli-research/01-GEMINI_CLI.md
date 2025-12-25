# Gemini CLI 详解

## 概述

Gemini CLI 是 Google 开源的 AI 代理工具，将 Gemini 的能力带入终端。

- **开源协议**：Apache-2.0
- **默认模型**：Gemini 2.5 Pro
- **上下文窗口**：1M tokens (业界最大)
- **免费额度**：60 次/分钟，1000 次/天

---

## 安装

```bash
# npm 安装
npm install -g @anthropic-ai/gemini-cli

# 或从 GitHub 安装
git clone https://github.com/google-gemini/gemini-cli.git
cd gemini-cli
npm install
npm install -g .
```

---

## 认证方式

### 方式 1：Google 账号 (免费)

```bash
gemini
# 首次运行会打开浏览器登录
```

### 方式 2：API Key

```bash
# 设置环境变量
export GEMINI_API_KEY="your-api-key"

# 或在 settings.json 中配置
```

### 方式 3：Vertex AI

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

---

## 配置文件

位置：`~/.gemini/settings.json`

```json
{
  "coreTools": {
    "shell": { "requireConfirmation": false },
    "file_write": { "requireConfirmation": false },
    "web_fetch": { "requireConfirmation": true }
  },
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"]
    }
  },
  "theme": "dark"
}
```

### 配置优先级

1. 项目级：`.gemini/settings.json`
2. 用户级：`~/.gemini/settings.json`
3. 系统级：`/etc/gemini-cli/settings.json`

---

## 核心功能

### 1. 内置工具

| 工具 | 功能 |
|------|------|
| Google Search | 网络搜索并引用结果 |
| File Operations | 文件读写操作 |
| Shell Commands | 执行终端命令 |
| Web Fetch | 获取网页内容 |

### 2. 多模态输入

```bash
# 拖放图片
gemini "分析这张截图" --image screenshot.png

# PDF 文档
gemini "总结这份报告" --file report.pdf

# 视频链接
gemini "分析这个视频" --url https://youtube.com/...
```

### 3. 斜杠命令

| 命令 | 功能 |
|------|------|
| `/help` | 帮助信息 |
| `/clear` | 清空对话 |
| `/model` | 切换模型 |
| `/tools` | 查看可用工具 |
| `/mcp` | MCP 服务器管理 |

---

## MCP 集成

### 添加 MCP 服务器

```bash
# CLI 方式添加
gemini mcp add memory -- npx -y @modelcontextprotocol/server-memory

# 列出已配置服务器
gemini mcp list

# 移除服务器
gemini mcp remove memory
```

### FastMCP 集成 (推荐)

```bash
# 安装 FastMCP 服务器到 Gemini CLI
fastmcp install gemini-cli
```

### 在对话中使用 MCP

```
@github List my open pull requests
@slack Send a summary to #dev channel
@database Query inactive users
```

---

## Docker 沙箱

Gemini CLI 默认使用 Docker 进行沙箱隔离。

### 默认沙箱

```bash
# 使用预构建镜像
gemini  # 自动使用 gemini-cli-sandbox 镜像
```

### 自定义沙箱

创建 `.gemini/sandbox.Dockerfile`：

```dockerfile
FROM gemini-cli-sandbox:latest

# 安装项目依赖
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install numpy pandas

WORKDIR /workspace
```

```bash
# 构建并使用自定义沙箱
BUILD_SANDBOX=1 gemini
```

### Docker MCP Toolkit

```bash
# 安装 Docker MCP Toolkit
docker extension install mcp-toolkit

# 配置 Gemini CLI 使用
gemini mcp add docker -- docker-mcp-gateway
```

---

## 与 Claude Code 集成

### 方案 1：Gemini 作为 MCP 服务器

创建 MCP wrapper 让 Claude Code 调用 Gemini：

```json
// ~/.claude/config.json
{
  "mcpServers": {
    "gemini": {
      "command": "gemini",
      "args": ["mcp-server"]
    }
  }
}
```

### 方案 2：使用第三方桥接

```bash
# 安装 gemini-mcp
npm i -g gemini-mcp-server

# 添加到 Claude Code
claude mcp add gemini -- npx gemini-mcp-server
```

---

## 常用命令

```bash
# 启动交互模式
gemini

# 执行单个任务
gemini "重构这个函数"

# 指定模型
gemini --model gemini-2.5-flash "快速任务"

# 安静模式 (脚本使用)
gemini --quiet "生成代码" > output.txt

# 查看版本
gemini --version
```

---

## 优势与局限

### 优势

- **1M 上下文窗口**：可处理大型代码库
- **免费额度慷慨**：个人使用完全免费
- **多模态最强**：图片、视频、PDF 支持
- **Google 生态集成**：Vertex AI、BigQuery、Cloud Functions
- **开源透明**：Apache-2.0 许可

### 局限

- 复杂推理不如 Claude
- Windows 支持有限
- 某些地区需要 VPN

---

## 参考资源

- [Gemini CLI 官方文档](https://google-gemini.github.io/gemini-cli/)
- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Gemini CLI 配置指南](https://geminicli.com/docs/get-started/configuration/)
- [FastMCP 集成博客](https://developers.googleblog.com/en/gemini-cli-fastmcp-simplifying-mcp-server-development/)
