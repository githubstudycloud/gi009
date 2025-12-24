import os
import json
import re
import argparse
import requests


def build_prompt(user_instruction):
    template = (
        "你是一个代码助手。用户希望你根据需求生成一个或多个文件。\n"
        "你必须只返回一个 JSON 对象，不能包含任何额外文字、说明或注释。\n"
        "JSON 结构为:\n"
        "{\n"
        "  \"files\": [\n"
        "    {\n"
        "      \"path\": \"相对于项目根目录的相对路径，例如 \\\"src/example.py\\\"\",\n"
        "      \"content\": \"文件的完整内容\"\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "请注意:\n"
        "1. 只生成需要新建或完全覆盖写入的文件内容。\n"
        "2. 不要使用绝对路径。\n"
        "3. 所有代码和文本都写在 content 字段中。\n"
        "4. 不要在 JSON 外多打一行文字。\n"
        "用户指令如下:\n"
        f"{user_instruction}\n"
    )
    return template


def call_ollama(model, prompt, base_url):
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a coding assistant. Always respond with pure JSON as instructed by the user.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "stream": False,
    }
    resp = requests.post(base_url + "/api/chat", json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    message = data.get("message") or {}
    content = message.get("content") or ""
    return content


def extract_json_block(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("模型输出中没有找到 JSON 对象")
    return json.loads(match.group(0))


def safe_join_generated(base_dir, relative_path):
    if os.path.isabs(relative_path):
        raise ValueError("不允许使用绝对路径")
    norm_path = os.path.normpath(relative_path)
    if norm_path.startswith(".."):
        raise ValueError("不允许访问项目根目录之外的路径")
    full_path = os.path.join(base_dir, "ai_generated", "code", norm_path)
    return full_path


def write_files(files, base_dir):
    written_paths = []
    for item in files:
        rel_path = item.get("path")
        content = item.get("content", "")
        if not rel_path:
            continue
        full_path = safe_join_generated(base_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        written_paths.append(full_path)
    return written_paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("instruction", help="自然语言的代码生成需求")
    parser.add_argument(
        "--project-root",
        default=os.getcwd(),
        help="项目根目录，默认当前目录",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b"),
        help="Ollama 模型名称",
    )
    parser.add_argument(
        "--ollama-url",
        default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        help="Ollama 服务地址",
    )
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    os.makedirs(os.path.join(project_root, "ai_generated", "code"), exist_ok=True)

    prompt = build_prompt(args.instruction)
    response_text = call_ollama(args.model, prompt, args.ollama_url)
    data = extract_json_block(response_text)
    files = data.get("files", [])
    if not files:
        print("模型没有返回 files 字段或为空")
        return

    written = write_files(files, project_root)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()

