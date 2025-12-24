# gi009 项目仓库

多人协作项目仓库，包含多个独立子项目。

## 📁 项目目录

### llm-api-deployment
支持 Claude Code 工具调用的开源大模型部署方案

- **功能**: 部署 Qwen2.5-Coder、DeepSeek-Coder 等支持 Function Calling 的大模型
- **部署方式**: Docker + vLLM / Ollama
- **特色**: CPU 推理、OpenAI API 兼容、完整中文文档
- **适用场景**: 代码生成、工具调用、1-10人团队使用

**快速开始**: [llm-api-deployment/QUICKSTART.md](./llm-api-deployment/QUICKSTART.md)

---

## 📝 添加新项目

如需添加新的子项目，请：

1. 在根目录创建新的子目录
2. 在子目录中组织项目文件
3. 更新本 README 添加项目说明
4. 提交更改

## 🤝 协作规范

- 每个子项目独立维护
- 各项目在各自目录内工作
- 根目录保持简洁，仅包含总览文档

## 📄 许可证

各子项目可使用独立的许可证，具体见各项目目录。
