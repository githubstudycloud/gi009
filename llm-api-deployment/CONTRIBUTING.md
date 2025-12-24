# 贡献指南

感谢你考虑为本项目做出贡献！


## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议，请：

1. **搜索现有 Issue**：确保问题尚未被报告
2. **创建新 Issue**：
   - 使用清晰的标题
   - 详细描述问题
   - 提供复现步骤
   - 附上环境信息（操作系统、Docker 版本等）
   - 如有错误日志，请附上

### 提交代码

1. **Fork 项目**

```bash
# 克隆你的 fork
git clone https://github.com/YOUR_USERNAME/gi009.git
cd gi009

# 添加上游仓库
git remote add upstream https://github.com/githubstudycloud/gi009.git
```

2. **创建分支**

```bash
# 从最新的 main 创建分支
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

分支命名规范：
- `feature/功能名` - 新功能
- `fix/问题描述` - Bug 修复
- `docs/文档名` - 文档更新
- `refactor/描述` - 代码重构

3. **进行修改**

- 保持代码风格一致
- 添加必要的注释
- 更新相关文档
- 编写测试（如适用）

4. **提交更改**

```bash
git add .
git commit -m "type: 简短描述

详细描述（可选）
- 改动点1
- 改动点2

相关 Issue: #123"
```

提交类型：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

5. **推送到 GitHub**

```bash
git push origin feature/your-feature-name
```

6. **创建 Pull Request**

- 清晰描述改动内容
- 关联相关 Issue
- 等待审核反馈


## 开发规范

### 代码风格

#### Docker Compose
- 使用 YAML 格式
- 适当缩进（2 空格）
- 添加必要的注释

#### Shell 脚本
- 使用 bash
- 添加 shebang: `#!/bin/bash`
- 使用 `set -e` 启用错误退出
- 添加注释说明

#### Python
- 遵循 PEP 8
- 使用类型注解
- 添加 docstring

#### Markdown
- 使用标准 Markdown 语法
- 中英文之间加空格
- 使用代码块标注语言

### 文档规范

- 使用清晰的标题层级
- 提供代码示例
- 包含必要的截图（如适用）
- 保持中文文档和英文文档同步
- 更新目录索引

### 测试

在提交前请：

1. **测试 Docker 配置**
```bash
docker-compose config
docker-compose up -d
docker-compose ps
docker-compose down
```

2. **测试脚本**
```bash
# Shell 脚本语法检查
shellcheck *.sh

# Python 脚本测试
python3 benchmark.py
```

3. **测试文档链接**
- 检查内部链接
- 验证外部链接
- 确保代码示例可运行


## 贡献领域

我们欢迎以下方面的贡献：

### 代码
- 新模型支持
- 性能优化
- Bug 修复
- 功能增强
- 测试用例

### 文档
- 改进现有文档
- 添加使用示例
- 翻译文档
- 视频教程

### 社区
- 回答 Issue
- 分享使用经验
- 撰写博客文章
- 推广项目


## 开发环境设置

### 本地开发

```bash
# 克隆项目
git clone https://github.com/githubstudycloud/gi009.git
cd gi009

# 创建配置
cp .env.example .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 运行测试

```bash
# API 测试
./test-api.sh

# 性能测试
python3 benchmark.py
```


## 提交前检查清单

- [ ] 代码通过所有测试
- [ ] 更新了相关文档
- [ ] 提交信息清晰明确
- [ ] 没有包含敏感信息
- [ ] 符合代码风格规范
- [ ] 更新了 CHANGELOG.md（如适用）


## Pull Request 审核流程

1. **自动检查**：CI/CD 会自动运行测试
2. **代码审查**：维护者会审查代码
3. **反馈修改**：根据反馈进行修改
4. **合并**：通过审核后合并到主分支


## 许可证

贡献的代码将在 [MIT License](./LICENSE) 下发布。

提交代码即表示你同意：
- 代码原创或有权贡献
- 接受 MIT 许可证


## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：
- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 人身攻击或侮辱性/贬损性评论
- 公开或私下骚扰
- 未经许可发布他人的私人信息
- 其他不道德或不专业的行为

### 执行

违反行为准则的行为可以向项目维护者报告。


## 获取帮助

如有疑问，请：

1. 查看 [文档](./README.md)
2. 搜索 [已有 Issue](https://github.com/githubstudycloud/gi009/issues)
3. 创建新 Issue 提问
4. 加入社区讨论


## 感谢

感谢所有贡献者！

你的贡献使这个项目变得更好。🎉


## 联系方式

- GitHub Issues: https://github.com/githubstudycloud/gi009/issues
- 项目主页: https://github.com/githubstudycloud/gi009


---

再次感谢你的贡献！❤️
