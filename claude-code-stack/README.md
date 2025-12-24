# claude-code-stack 使用说明

这是一个“Claude Code 风格”的本地大模型辅助目录，用来：

- 在子目录里部署/连接本地大模型（Ollama + Open WebUI）
- 通过脚本把模型生成的代码集中写到 `ai_generated/code` 子目录，避免直接改动主工程代码

当前仓库相关文件：

- `claude-code-stack/docker-compose.yml`：Ollama + Open WebUI 部署模板
- `claude-code-stack/client/main.py`：代码生成客户端脚本（Claude Code 风格）

---

## 一、前提条件

- 已经有一台跑 Ollama 的机器（推荐 Ubuntu，CPU 内存够即可）
- 或者本机已经安装并启动了 Ollama，监听 `http://localhost:11434`
- Python 3.8+，并安装 `requests` 库

在当前仓库根目录（例如 `d:\tr1`）执行：

```bash
pip install requests
```

---

## 二、代码生成脚本使用方式

脚本位置：`claude-code-stack/client/main.py`

脚本作用：

- 接受一段自然语言需求
- 调用本地 Ollama 上的模型（默认 `qwen2.5-coder:7b`）
- 要求模型返回一个 JSON，包含要生成的文件列表
- 把这些文件统一写入：
  - `<项目根目录>/ai_generated/code/<模型返回的相对路径>`

### 1. 基本用法（在当前仓库根目录）

在 `d:\tr1` 下打开终端：

```bash
cd d:\tr1
python .\claude-code-stack\client\main.py "写一个 Python 程序，文件名为 examples/hello.py，打印一句话"
```

运行成功后，生成文件会出现在：

```text
d:\tr1\ai_generated\code\examples\hello.py
```

可以用 Python 运行它：

```bash
python .\ai_generated\code\examples\hello.py
```

### 2. 指定项目根目录

如果你要在其他项目里使用同一个脚本，可以通过 `--project-root` 指定根目录：

```bash
python .\claude-code-stack\client\main.py ^
  "生成一个 calc/calculator.py，包含加减乘除四个方法" ^
  --project-root "d:\my-project"
```

生成的文件会在：

```text
d:\my-project\ai_generated\code\calc\calculator.py
```

### 3. 指定模型和 Ollama 地址

默认配置：

- 模型：`qwen2.5-coder:7b`
- Ollama 地址：`http://localhost:11434`

如果你的 Ollama 在别的机器上，例如 `http://192.168.1.10:11434`，可以在终端里先设置环境变量：

```bash
set OLLAMA_BASE_URL=http://192.168.1.10:11434
set OLLAMA_MODEL=qwen2.5-coder:7b
```

然后再运行脚本：

```bash
python .\claude-code-stack\client\main.py "写一个包含类和单元测试的示例"
```

---

## 三、生成文件的规则（Claude Code 风格）

- 模型只负责“提案”，即返回 JSON，内容类似：

  ```json
  {
    "files": [
      {
        "path": "examples/hello.py",
        "content": "print('hello')\n"
      }
    ]
  }
  ```

- 真实写盘的是 `main.py` 脚本，并强制：
  - 所有路径都拼到 `ai_generated/code` 下面
  - 禁止绝对路径
  - 禁止使用 `..` 跑出项目根目录

这可以保证：

- 不会直接覆盖你现有的 `src/`、`docs/` 等正式代码
- 你可以从 `ai_generated/code` 里挑选满意的文件再手动移到正式目录

---

## 四、docker-compose 模板说明

文件：`claude-code-stack/docker-compose.yml`

它是一个参考用的部署模板，提供：

- `ollama` 服务（本地大模型服务）
- `open-webui` 服务（Web 界面，多用户聊天）

如果你在 Ubuntu 上部署，可以：

```bash
mkdir -p ~/claude-code-stack
cp docker-compose.yml ~/claude-code-stack/
cd ~/claude-code-stack
docker compose up -d
```

然后在能访问这台机器的任意地方，设置：

```bash
set OLLAMA_BASE_URL=http://<你的服务器IP>:11434
```

再运行 `client/main.py` 即可。

---

## 五、最小化测试步骤总结

1. 确认 Ollama 已经在某台机器上运行，并且能访问 `http://<IP>:11434`
2. 在当前仓库根目录安装依赖：

   ```bash
   pip install requests
   ```

3. 在终端运行一次示例命令：

   ```bash
   cd d:\tr1
   python .\claude-code-stack\client\main.py "写一个 examples/hello.py，打印 Hello Claude Style"
   ```

4. 在 `ai_generated\code` 目录下找到生成的文件并运行测试。

