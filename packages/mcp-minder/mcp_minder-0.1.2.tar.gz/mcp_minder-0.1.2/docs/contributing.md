# 贡献指南

感谢您对 MCP Minder 项目的关注！我们欢迎所有形式的贡献。

## 如何贡献

### 报告问题

如果您发现了bug或有功能建议，请：

1. 检查是否已有相关Issue
2. 创建新的Issue，包含：
   - 清晰的问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息

### 提交代码

1. **Fork 项目**
2. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **提交更改**
   ```bash
   git commit -m "feat: 添加新功能"
   ```
4. **推送分支**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **创建 Pull Request**

## 代码规范

### 提交信息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 代码风格

- 使用 Black 进行代码格式化
- 使用 isort 排序导入语句
- 遵循 PEP 8 规范
- 添加适当的类型注解
- 编写清晰的文档字符串

### 测试要求

- 新功能必须包含测试
- 测试覆盖率不应降低
- 所有测试必须通过

## 开发流程

### 1. 设置开发环境

```bash
# 克隆项目
git clone <repository-url>
cd mcp-minder

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装开发依赖
make install-dev
```

### 2. 开发

```bash
# 创建功能分支
git checkout -b feature/your-feature

# 进行开发...

# 运行质量检查
make all
```

### 3. 提交

```bash
# 添加更改
git add .

# 提交
git commit -m "feat: 添加新功能"

# 推送
git push origin feature/your-feature
```

## 文档贡献

### 更新文档

- README.md: 项目概述和快速开始
- docs/: 详细文档
- 代码注释: 函数和类的文档字符串

### 文档规范

- 使用 Markdown 格式
- 保持简洁明了
- 包含代码示例
- 定期更新

## 社区准则

### 行为准则

- 保持友善和尊重
- 欢迎不同观点
- 专注于对项目最有利的事情
- 尊重不同的观点、经验和技能水平

### 沟通

- 使用中文或英文
- 保持专业和礼貌
- 提供清晰的反馈
- 及时响应

## 发布流程

### 版本管理

项目使用 [语义化版本](https://semver.org/)：

- `MAJOR`: 不兼容的API更改
- `MINOR`: 向后兼容的功能添加
- `PATCH`: 向后兼容的bug修复

### 发布步骤

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建发布标签
4. 构建和发布包

## 获取帮助

如果您在贡献过程中遇到问题：

1. 查看项目文档
2. 搜索现有Issue
3. 创建新Issue
4. 参与讨论

## 致谢

感谢所有为项目做出贡献的开发者！

您的贡献让这个项目变得更好。
